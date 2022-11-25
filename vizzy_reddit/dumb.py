from random import *
import requests

from utils import *

from datetime import *
import pytz
import discord

from discord import SyncWebhook




def craft_embed(title, user_comment, webhook, url, thumbnail, response, color=0x00ff00):


    e = discord.Embed(title=title, description=user_comment,
                      url=url,
                      color=color)

    e = e.add_field(name="Response:", value=response, inline=True)

    e = e.set_thumbnail(url=thumbnail)

    webhook = SyncWebhook.from_url(webhook)

    webhook.send(embed=e)

    return e

class VIZZY_T:
    def __init__(self):

        # Load in credentials from .env
        load_dotenv()

        print("Cunt")

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
        self.webhook_bofh = os.getenv('webhook_bofh')
        self.webhook_canon = os.getenv('canon_vizzy')
        self.webhook_sentient = os.getenv('sentient_vizzy')

        self.sentience_whitelist = ['apostastrophe','limacy','invertiguy','adelledewitt']



        self.webhook_babysitter = os.getenv('webhook_babysitter')

        # Set the subreddit to monitor
        self.subreddit = self.reddit.subreddit('vizzy_t_test+freefolksimulator+freefolk+HouseOfTheDragon+asofiaf+BSFT+stonkymemes+SoapBoxBeers+biscuit_meltdown+shitboxbeers+hotd+hotdgreens+asoifcirclejerk')
        # self.subreddit = self.reddit.subreddit('freefolksimulator_TST')

        # Pull in quotes from quotes.py
        self.quotes = quotes

        self.tz = pytz.timezone('US/Eastern')


        # Set the subreddit stream to comments and posts
        self.stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(self.subreddit, **kwargs))


    def send_errors(self, body, comment=None):
        """Use webhooks to notify admin on Discord

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
                body += "\nLord Tyrion has apologized for the crown."""


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

    def send_webhook(self, body, sentient=False):
        # self.webhook_sentient

        if sentient:
            url = self.webhook_sentient
            data = {'content': body, 'username': 'Sentient Vizzy T'}
        else:
            url = self.webhook_babysitter
            data = {'content': body, 'username': 'FFS Babysitter'}

        requests.post(url, data=data)


    """Sending a normal, random response"""
    def response_canon(self,comment):
        ts = datetime.now(self.tz)
        if ((ts.hour == 23 and ts.minute > 30) or (ts.hour == 0 and ts.minute < 30)) and isComment(comment):
            response, cost = get_sentient(comment)
            comment.reply(body=response)
            # comment.upvote()
            writeComment(comment.id)

            user_comment = f"{comment.author.name}: {self.getText(comment)}"
            webhook =self.webhook_sentient
            url = f'https://www.reddit.com{comment.permalink}'
            thumbnail = 'https://thc-lab.net/ffs/vizzy-t-bot.jpeg'

            craft_embed("Vizzy T", user_comment, webhook, url, thumbnail, response, color=0x00ff00)


        else:

            try:
                seed()
                num = randint(0, len(quotes) - 1)
                response = quotes[num]
                if "{}" in response:
                    response = response.format(comment.author.name)

                comment.reply(body=response)
                # comment.upvote()
                writeComment(comment.id)

                user_comment = f"{comment.author.name}: {self.getText(comment)}"
                webhook = self.webhook_canon
                url = f'https://www.reddit.com{comment.permalink}'
                thumbnail = 'https://thc-lab.net/ffs/vizzy-t-bot.jpeg'

                craft_embed("Vizzy T", user_comment, webhook, url, thumbnail, response, color=0x00ff00)


            except Exception as e:
                #body = "https://www.reddit.com"+comment.permalink + " - " + str(e)
                self.send_errors(e)




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

        if (not isComment(redditObject)) and (redditObject.link_flair_text == "fuck off bots"):
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

        return redditObject.body.lower()


    """Get all the info we need about a post to respond to it"""
    def post_processer(self, redditObject):

        user_text = redditObject.title.lower() + "\n" + redditObject.selftext.lower()

        return user_text


    """Splitting up between comments and posts, uses the above two functions"""
    def firstlook(self, redditObject):
        # Gather needed info if it's a comment
        if isComment(redditObject):
            user_text = self.comment_processer(redditObject)

        # Gather information if it's a comment
        else:
            user_text = self.post_processer(redditObject)


        is_triggered = triggered(user_text)

        return user_text, is_triggered


    def debug(self,comment):
        '''This executes when Steve comments saying "Why didn't you respond here, Vizzy?"'''

        parent = comment.parent()

        parent.refresh()

        in_db = parent.id in getComments()


        if in_db:

            parent.replies.replace_more()

            child_comments = parent.replies.list()
            for child_comment in child_comments:
                if child_comment.author.name.lower() == "vizzy_t_bot":
                    url = f"https://www.reddit.com{child_comment.permalink}"
                    reply = f"[It's right here, smartass.]({url})"
                    comment.reply(body=reply)
                    return
        else:

            user_text, residual_sentience = self.comment_processer(parent)


            is_triggered = triggered(user_text)

            is_depleted = parent.id in getCommentsdwarf()

            report = f"Comment by {parent.author.name}\n\nResidual Sentience: {str(residual_sentience)}\n\nComment ID in response database: {str(in_db)}\n\nComment ID in depleted database: {str(is_depleted)}\n\nTriggered? {str(is_triggered)}\n\n"

            if not residual_sentience and not is_triggered:
                note = "*This comment did not contain trigger words, and was not a reply to a comment with residual sentience.*"
            elif residual_sentience and is_depleted and not is_triggered:
                note = "*This comment did not contain trigger words.  It was a reply to a comment that had residual sentience, but it was used by another Redditor.*"
            else:
                note = "*I am not sure why this comment was not processed, sorry.  Would you like to see the tapestries?*"

            final = report + note

            comment.reply(body=final)



    """Primary Function"""
    def vizzytime(self, redditObject):

        skip = self.base_response_checks(redditObject)

        if skip:
            print(f"Skipping https://www.reddit.com{redditObject.permalink}")
            return

        else:
            user_text, triggered = self.firstlook(redditObject)

            if triggered:
                if str(redditObject.author.name.lower()) in self.sentience_whitelist:
                    r,c = get_sentient(redditObject)
                    redditObject.reply(body=r)
                    writeComment(redditObject.id)

                    user_comment = f"{redditObject.author.name}: {self.getText(redditObject)}"
                    webhook = self.webhook_sentient
                    url = f'https://www.reddit.com{redditObject.permalink}'
                    thumbnail = 'https://thc-lab.net/ffs/vizzy-t-bot.jpeg'

                    craft_embed("Sentient Vizzy T", user_comment, webhook, url, thumbnail, r, color=0x00ff00)

                elif str(redditObject.author.name.lower()) == "sober-lab":
                    r,c = get_sentient(redditObject)
                    redditObject.reply(body=r)
                    writeComment(redditObject.id)

                    user_comment = f"{redditObject.author.name}: {self.getText(redditObject)}"
                    webhook = self.webhook_sentient
                    url = f'https://www.reddit.com{redditObject.permalink}'
                    thumbnail = 'https://thc-lab.net/ffs/vizzy-t-bot.jpeg'

                    craft_embed("Sentient Vizzy T", user_comment, webhook, url, thumbnail, r, color=0x00ff00)

                else:
                    '''
                    If there's a normal Vizzy T trigger on a non-sentient post
                    
                    He'll evaluate sentience and then make a normal response or a sentient response.
                    '''
                    print(f"Triggered, on https://www.reddit.com{redditObject.permalink}")
                    self.response_canon(redditObject)

            # Get triggered by just that phrase, mostly used so Vizzy can talk to Bobby.  Was requested.
            elif "the whore is pregnant!" in user_text:

                # Yell at Bobby B.
                x = whore()
                redditObject.reply(body=x)

    def run(self):
        for comment in self.subreddit.stream.comments():
            if comment.body == "Why didn't you respond here, Vizzy?" and comment.author.name in ['SOBER-Lab','LSA-Lab']:
                self.debug(comment)
            else:
                try:
                    self.vizzytime(comment)
                except Exception as e:
                    body = f"Vizzy T Error Report:\n{e}"
                    self.send_errors(body,)


# GODS BE GOOD
vt = VIZZY_T().run()
