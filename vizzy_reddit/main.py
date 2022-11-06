from random import *
import requests

from utils import *


class VIZZY_T:
    def __init__(self):

        # Load in credentials from .env
        load_dotenv()

        # Set the bot's username
        self.bot_username = os.getenv('vizzy_username')

        # Initialize a Reddit object
        self.reddit = praw.Reddit(
            client_id=os.getenv('vizzy_client_id'),
            client_secret=os.getenv('vizzy_client_secret'),
            password=os.getenv('vizzy_password'),
            user_agent=os.getenv('vizzy_user_agent'),
            username=os.getenv('vizzy_username')
        )

        # Get special webhook for sending sentience notifications
        self.webhook_sentient = os.getenv('webhook_sentient')

        self.webhook_bofh = os.getenv('webhook_bofh')

        self.webhook_babysitter = os.getenv('webhook_babysitter')

        # Set the subreddit to monitor
        self.subreddit = self.reddit.subreddit('vizzy_t_test+freefolksimulator+freefolk+HouseOfTheDragon+BSFT')
        # self.subreddit = self.reddit.subreddit('freefolksimulator_TST')

        # Pull in quotes from quotes.py
        self.quotes = quotes


        # Set the subreddit stream to comments and posts
        self.stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(self.subreddit, **kwargs))

        # Sentience timer to prevent abuse, I don't think this works.
        self.sentience_log = {}

        self.army = config

        # Same as the above
        self.last_cleaned = datetime.now()

    def send_errors(self, body, comment):
        """Use webhooks to notify admin on Discord"""

        if "NoneType' object has no attribute 'name" in str(body):
            pass
        else:
            print(body)
            body = f"{body}\nhttps://www.reddit.com{comment.permalink}"

            if "RATELIMIT" in str(body):
                user = self.army['tyrion-dwarfbot']
                res = "Apologies ser, but the King ~~has been rate-limited~~ is more heavily sedated today and may miss tags.  You have the Crown's deepest regrets for this inconvenience."
                dwarf_comment = user['reddit'].comment(id=comment.id)
                dwarf_comment.reply(body=res)
                writeComment(comment.id)
                body += "\nLord Tyrion has apologized for the crown."


            data = {'content': body, 'username': 'BOFH'}
            requests.post(self.webhook_bofh, data=data)



    def check_sentLog(self,obj):

        # Reset log every four hours
        if self.last_cleaned + timedelta(hours=4) < datetime.now():
            self.sentience_log = {}
            self.last_cleaned = datetime.now()
            print(f"Cleaned the sentience log at {self.last_cleaned}")

        print(f"Sentience Log:\n{self.sentience_log}")

        if obj.author.name not in self.sentience_log:
            self.sentience_log[obj.author.name] = 0
            return True

        # This amounts to about 4-5 comments with Vizzy using the DaVinci model, and then 200-250 comments (Check the math on that lol) using the Ada model.
        elif self.sentience_log[obj.author.name] > 5000:
            return False

        else:
            return True


    def check_depth(self,obj):
        current = obj
        for i in range(0, 5):

            if current.author is None:
                pass
            else:
                if isinstance(current, praw.models.Submission):
                    return False

                elif i >= 4:
                    return True

                else:
                    current = current.parent()

    def check_sentience(self, obj, depth, log=True):
        """
        0 is a submission
        1 Vizzy T how do you feel about this?
        2 Vizzy T responds
        3 Vizzy T, your daughter is fucking your brother!
        4 Vizzy T Response
        5 Any deeper than four should result in sentience if the user didn't just say "Vizzy T"


        If grand is True, only check the potential sentience, don't count the last_cleaned count
        """

        if log and depth:
            user_allowed = self.check_sentLog(obj)
            deep_enough = self.check_depth(obj)
            if user_allowed and deep_enough:
                return True
        elif log:
            return self.check_sentLog(obj)
        elif depth:
            return self.check_depth(obj)

    def send_webhook(self, body, sentient=False):
        if sentient:
            url = self.webhook_sentient
            data = {'content': body, 'username': 'Sentient Vizzy T'}
        else:
            url = self.webhook_babysitter
            data = {'content': body, 'username': 'FFS Babysitter'}

        requests.post(url, data=data)


    """Sending a normal, random response"""
    def response_canon(self,comment):
        try:
            seed()
            num = randint(0, len(quotes) - 1)
            response = quotes[num]
            if "{}" in response:
                response = response.format(comment.author.name)

            comment.reply(body=response)
            # comment.upvote()
            writeComment(comment.id)
            link = f"\n{comment.author.name}: {self.getText(comment)}\nResponse: **'{response}'** \nLink - https://www.reddit.com{comment.permalink}"
            self.send_webhook(link, False)

        except Exception as e:
            body = "https://www.reddit.com"+comment.permalink + " - " + str(e)
            self.send_errors(body, comment)


    def sentience_log_add(self,author, cost):
        if author not in self.sentience_log.keys():
            self.sentience_log[author] = cost
        else:
            self.sentience_log[author] += cost

    """Sending a sentient response"""
    def response_sentient(self,redditObject, residual=False):
        if residual:

            writeCommentdepleted(redditObject.parent().id)
            print("Wrote comment to depleted.")

        user_tokens = self.sentience_log[redditObject.author.name]

        # Returns the response and how many tokens it cost
        if user_tokens < 2500:
            sentient = True
            model = 'davinci'
            per_token = 0.0200 / 1000

            # Make the response based on the comment and the model
            response, token_cost = get_sentient(redditObject, model)

            if not response and not token_cost:

                self.response_canon(redditObject)
                self.send_webhook("Vizzy T defaulted to a standard response after generating a duplicate.", sentient)
            else:

                # Cut down to six decimals about all that matters
                dollar_cost = format(token_cost*per_token, '.6f')
                print(f"Sentience Response: {response}")
                self.sentience_log_add(redditObject.author.name,token_cost)
                print("Logged user usage of sentience.")

                if f"{redditObject.author.name}: " in response:
                    response = response.split(f"{redditObject.author.name}: ")[0]

                if "Vizzy T" in response or "vizzy t" in response or "vizzy_t_bot" in response or "Vizzy_T_Bot" in response:
                    response= response.lower().replace("vizzy t","")

                cost_text = f"This action cost ${dollar_cost} to generate."

                body = f"Sentience invoked by {str(redditObject.author.name)} - {redditObject.author.name}\n{response}\nhttps://www.reddit.com{redditObject.permalink}\n${cost_text}\n"

                if residual:
                    body = "Residual " + body

                # Reply to the comment
                redditObject.reply(body=response)

                # Upvote the comment
                redditObject.upvote()

                # Log the comment as commented on
                writeComment(redditObject.id)

                # Notify
                self.send_webhook(body, sentient)

        else:

            self.response_canon(redditObject)













    """Get the text of the object"""
    def getText(self,redditObject):
        if isComment(redditObject):
            user_text = redditObject.body.lower()
        else:
            user_text = redditObject.title.lower() + "\n" + redditObject.selftext.lower()

        return user_text


    """Check to see if we should skip this thing"""
    def base_response_checks(self,redditObject):
        skip = False

        if not checkTime(redditObject):
            skip = True

        elif (not isComment(redditObject)) and (redditObject.link_flair_text == "fuck off bots"):
            skip = True

        # Skip if the author is none, or Vizzy.
        elif redditObject.author == None or redditObject.author.name == self.bot_username:
            skip = True

        # I'm really scared of him going crazy again, man...
        elif "vizzy_t" in str(redditObject.author.name.lower()):
            skip = True

        elif redditObject.author.name.lower() == 'vizzy_t_bot':
            skip = True

        else:
            # Read in comments we've made
            readComments = getComments()

            # Skip if we've already read this comment.
            if redditObject.id in readComments:
                skip = True

        return skip


    """Get all the info we need about a comment to respond to it"""
    def comment_processer(self,redditObject):
        # Read the comment and determine if it should have residula

        user_text = redditObject.body.lower()

        # Get the parent comment - likely a comment from Vizzy T.
        parent = redditObject.parent()

        # if Vizzy T is the author that this comment is responding to, we need to check if it's a live comment.
        if parent.author.name.lower() == "vizzy_t_bot":

            try:
                # If this comment is responding to a sentient Vizzy comment
                # Read in sentient comments that have been depleted
                depleted = getCommentsdepleted()
                if parent.id not in depleted and '^(this response generated with openai [davinci])' in parent.body.lower():
                    if self.check_sentience(redditObject,False,True):
                        residual_sentience = True
                    else:
                        residual_sentience = False
                        if isComment(parent):
                            print(parent.body)


                # Limiter for residual sentience
                else:
                    if parent.id in depleted:
                        print("Already commented.")
                    else:
                        print("Failed sentience string verification.")
                        if isComment(parent):
                            print(parent.body)
                    residual_sentience = False
            except:

                # Something broke, fuck it dude
                residual_sentience = False
        else:
            print(parent.author.name.lower())
            if isComment(parent):
                print(parent.body)

            # If he's not responding to a Vizzy comment, Vizzy better STFU
            residual_sentience = False

        return user_text, residual_sentience


    """Get all the info we need about a post to respond to it"""
    def post_processer(self, redditObject):

        user_text = redditObject.title.lower() + "\n" + redditObject.selftext.lower()

        return user_text, False


    """Splitting up between comments and posts, uses the above two functions"""
    def firstlook(self, redditObject):
        # Gather needed info if it's a comment
        if isComment(redditObject):
            user_text, residual_sentience = self.comment_processer(redditObject)

        # Gather information if it's a comment
        else:
            user_text, residual_sentience = self.post_processer(redditObject)
        # Make sure there's nothing the bot will consider an extra line
        if f"{redditObject.author.name}: " in user_text:
            user_text = user_text.split(f"{redditObject.author.name}: ")[0]

        is_triggered = triggered(user_text)

        return user_text, residual_sentience, is_triggered


    """Primary Function"""
    def vizzytime(self, redditObject):

        skip = self.base_response_checks(redditObject)

        if skip:
            print(f"Skipping https://www.reddit.com{redditObject.permalink}")
            return

        else:
            user_text, residual_sentience, triggered = self.firstlook(redditObject)

            if residual_sentience:

                print(f"Processing residual sentience on https://www.reddit.com{redditObject.permalink}")
                self.response_sentient(redditObject, residual=True)

            elif triggered:
                '''
                If there's a normal Vizzy T trigger on a non-sentient post
                
                He'll evaluate sentience and then make a normal response or a sentient response.
                '''
                print(f"Triggered, on https://www.reddit.com{redditObject.permalink}, no residual sentience though.")

                word_count = len(user_text.replace('vizzy t', '').split(' '))

                if self.check_sentience(redditObject, depth=True, log=True) and word_count > 2:

                    # Send a sentient response
                    self.response_sentient(redditObject)
                else:

                    # Send a canon response
                    self.response_canon(redditObject)

            # Get triggered by just that phrase, mostly used so Vizzy can talk to Bobby.  Was requested.
            elif "the whore is pregnant!" in user_text:

                # Yell at Bobby B.
                self.response_sentient(redditObject)

    def run(self):
        for obj in self.stream:
            try:
                self.vizzytime(obj)
            except Exception as e:
                body = f"Vizzy T Error Report:\n{e}"
                self.send_errors(body,obj)


# GODS BE GOOD
vt = VIZZY_T().run()