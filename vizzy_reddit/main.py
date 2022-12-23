from modules.cloud_sql import *
from modules.utils import *
import pytz
from random import *


class VIZZY_T:
    def __init__(self):

        # Are we running in production or testing?
        self.production = is_production()

        # Set the bot's username
        self.bot_username = os.getenv('vizzy_t_bot')

        # Load in Vizzy and Tyrion
        self.all_bots = makeBots()

        # Grab the quotes
        self.quotes = self.all_bots['vizzy_t_bot']['quotes']

        # Set default Reddit object to be Vizzy's Reddit
        self.reddit = self.all_bots['vizzy_t_bot']['r']

        # Load in local config, and configure the subreddit.
        self.config_load()

        # Initialize the Maester of Webhooks from utils.py
        self.MoW = webhookmaster()

        # Initialize cloud database
        self.db = db()

    def make_comment(self,comment, response):

        comment.reply(body=response)

        self.db.write_obj(comment.id, 'vizzy_t_bot')

    def make_subs(self):
        """ Get a text-based list of the subreddits we should be watching based on the bot's location """
        if not self.production:

            return 'vizzy_t_test'

        else:

            # Get a list of the subreddit types
            sub_categories = self.config['subreddits'].keys()

            # Empty list for subreddits to crawl
            subs = []

            # Iterate through the subreddit categories
            for category in sub_categories:

                # Skip vizzy_t_test if we're in production
                if self.production and category == 'test':
                    pass

                else:
                    # Add subs to list of subs we should listen to
                    subs += self.config['subreddits'][category]

            sublist = '+'.join(subs)

            return sublist

    def config_load(self):
        """ Load in local configuration from a json, initialize Reddit stuff """

        # Read in the json file
        with open('config.json', 'r') as file:
            data = file.read()
            self.config = json.loads(data)

        # Get the (string) of subs to follow
        self.sub_list = self.make_subs()

        # Turn them into a subreddit object
        self.subreddit = self.reddit.subreddit(self.sub_list)

        # Set the subreddit stream to comments and posts
        self.stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(self.subreddit, **kwargs))

        # Grab the timezone
        self.tz = pytz.timezone(self.config['timezone'])

        print("Configuration loaded successfully, Reddit initialized.")


    def funny_business(self,text):
        """ Easter Eggs go here. """

        # Woohoo Hot fuzz
        if "got a mustache" in text:
            return "mustache"

        elif "the whore is pregnant" in text:
            return "whore"

        else:
            return "None"


    def get_details(self, object):
        """ Load the details of a post / comment, helpful for keeping Vizzy from crashing on deleted things """

        # Get the author name
        author = object.author.name.lower()

        # Get the author name
        author_original = object.author.name

        if self.skip_checker(author,object.id):
            return False, False, False, False, False, False, False

        else:

            # If this is a comment, grab the comment body
            if isComment(object):

                text = object.body

            else:

                text = object.title + "\n" + object.selftext


            text = text.lower()

            permalink = f'https://www.reddit.com{object.permalink}'

            triggered = ("vizzy t" in text or "vissy t" in text)

            funny = self.funny_business(text)

            return author, author_original, text, permalink, object.id, triggered, funny


    def sentience_checker(self,author, text):
        """Check if a response should be sentient.  Takes multiple factors into consideration."""

        # If Sentience is disabled in the config, we won't be sentient.  Still allows for Maesters.
        if self.config['sentience'] == 'false' and author not in self.config['maesters']:
            return False

        # If the author is in the sentience whitelist, go ahead and be sentient.
        elif author in self.config['sentience_whitelist']:
            return True

        # Allow sentient responses to Maesters if they're using italics
        elif author in self.config['maesters'] and text.count("*") >= 2:
            return True

        # If the sentience limiter is enabled, check and see if it's the appropriate time.      iyybaaq
        elif self.config['sentience'] == 'true' and self.config['sentience_limiter'] == 'true':

            # Get current timestuff
            ts = datetime.now(self.tz)
            h = ts.hour
            m = ts.minute

            # Do calculations
            waking_up = (h == self.config['wakeup'][0] and m > self.config['wakeup'][1])
            going_to_sleep = (h == self.config['sleep'][0] and m < self.config['sleep'][1])

            # This is a little better, but still static in the sense that it won't work unless it's 11PM-12AM.
            # Check if it's between the specified times in config and if Vizzy should be sentient or not
            if (waking_up) or (going_to_sleep):
                return True

            else:
                return False

        else:
            return False

    def pull_quote(self, author):
        """Sending a normal, random response"""

        # Seed the randomness
        seed()

        # Grab a quote
        response = self.quotes[randint(0, len(self.quotes) - 1)]

        # Fill in user's username if applicable to this quote
        if "{}" in response:
            response = response.replace("{}", author)

        return response


    def skip_checker(self,author,id):
        """Check to see if we should skip this thing"""

        # Skip if the author is None (Someone deleted something)
        if author is None:
            return True

        # Skip if the author is vizzy_t_bot
        elif author == self.bot_username:
            return True

        # Skip if the comment ID is in the database already
        elif self.db.check_db(id, 'vizzy_t_bot'):
            return True

        # Otherwise, don't skip.
        else:
            # print(f"This {id} has a valid author, and is not in the database")
            return False


    def vizzytime(self, redditObject, author, text):
        """Primary function, processes everything"""

        # If we should be sentient...
        if self.sentience_checker(author.lower(), text):

            # Get a sentient response and associated cost
            response, cost = get_sentient(redditObject)
            description = "Vizzy T made a sentient comment"
            self.db.usage_dump(author, author, "Vizzy T Sentience",text, author, text, cost)


        else:

            # Generate the bot's response
            response = self.pull_quote(author)
            cost = None
            description = "Vizzy T made a canon comment"

        # Check if Vizzy should show off his tapestries
        if 'tapestries' in response.lower():
            image_url = WOULDYOULIKETOSEETHETAPESTRIES(redditObject.author.name)
            response = f"[{response}]({image_url})"
            description += ", and showed off his tapestries!"
            self.db.usage_dump(author, author, "Vizzy T Sentience",text, author, text, cost)

        else:
            description += "."


        self.make_comment(redditObject, response)
        self.db.write_obj(redditObject.id, "vizzy_t_bot")

        print("Dumped comment!")

        return response, cost, description

    def run(self):

        # Iterate through all the posts / comments
        for object in self.stream:

            requests.get('https://hc-ping.com/9d4dd9b0-7d3d-4694-8704-aa207c346793')

            try:

                # Grab info from the thing
                author, author_original, text, permalink, comment_id, is_triggered, deviant = self.get_details(object)

                if not author and not text and not is_triggered:

                    pass

                else:
                    if deviant == "mustache":
                        print("Processing this post because it has a mustache.")

                        response = '[*...I know.*](https://thc-lab.net/static/i-know.gif)'

                        object.reply(body=response)

                        self.db.write_obj(comment_id, "vizzy_t_bot")



                        self.MoW.craft_embed(description="FUCK YEAH HOT FUZZ.",
                                             url=permalink,
                                             author=author_original,
                                             comment=text,
                                             response=response)




                    # Skip if we're not triggered
                    elif not is_triggered:
                        pass

                    # We are triggered and nothing else interesting should happen.
                    else:
                        print("We're processing this post because no one told us not to!")

                        # Reply to the comment
                        response, cost, description = self.vizzytime(object, author_original, text)

                        # Send an embed to Discord
                        self.MoW.craft_embed(description=description,
                                             url=permalink,
                                             author=author_original,
                                             comment=text,
                                             response=response)

            except Exception as e:

                # Send errors to Discord
                print(e)
                self.MoW.send_errors(e=e,
                                     url=f'https://reddit.com{object.permalink}',
                                     comment=object)

# GODS BE GOOD
vt = VIZZY_T().run()
