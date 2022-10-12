import os
from datetime import *
from random import *

import praw
import requests
from dotenv import load_dotenv

from quotes import quotes
from sql import *


class VIZZY_T:
    def __init__(self):

        # Load in credentials from .env
        load_dotenv()

        # Set the bot's username
        self.bot_username = os.getenv('reddit_username')

        self.webhook_url = os.getenv('webhook')

        # Initialize a Reddit object
        self.reddit = praw.Reddit(
            client_id=os.getenv('client_id'),
            client_secret=os.getenv('client_secret'),
            password=os.getenv('password'),
            user_agent=os.getenv('user_agent'),
            username=self.bot_username
        )

        # Set the subreddit to monitor
        self.subreddit = self.reddit.subreddit('vizzy_t_test+soapboxbeers+freefolk')

        # Pull in quotes from quotes.py
        self.quotes = quotes

        # Special quote for some reason
        self.final_quote = '"I, Viserys Targaryen, first of his name... King of the Andals, and the Rhoynar, and the First Men, ' \
                           'Lord of the Seven Kingdoms, and Protector of the Realm, do hereby name...' \
                           '{} Princess of Dragonstone and heir to the Iron Throne.'
        self.hf = ["IT'S ALRIGHT ANDY! IT'S JUST BOLOGNESE!", "Don't you go bein' a twat now", 'Two blokes and a fuck-load of cutlery!']

        # Lazy variables for noting used quotes to keep from using them again within the hour
        self.posted = []
        self.posted_hour = datetime.now().hour

        # GODS BE GOOD
        self.run()

    def send_webhook(self, body):
        """Use webhooks to notify admin on Discord"""
        data = {'content': body, 'username': 'VIZZY-T-BOT'}
        requests.post(self.webhook_url, data=data)

    def vizzytime(self, redditObject, type):
        readComments = getComments()
        if redditObject.author == None:
            pass
        elif redditObject.id in readComments or redditObject.author.name == self.bot_username:
            pass
        else:
            if type == "comment":
                to_check = redditObject.body.lower()
            else:
                to_check = redditObject.selftext.lower() + " " + redditObject.title.lower()

            if "vizzy t" in to_check or "vissy t" in to_check:
                response = ""
                while not response:
                    seed()
                    num = randint(0, len(self.quotes) - 1)
                    if datetime.now().hour != self.posted_hour or len(self.posted) > len(self.quotes) - 5:
                        self.posted = []
                        self.posted_hour = datetime.now().hour

                    if num in self.posted:
                        pass
                    else:
                        if "hot fuzz" in to_check:
                            num = randint(0, len(self.hf) - 1)
                            response = self.hf[num]
                        else:
                            response = self.quotes[num]
                        if "{}" in response:
                            response = response.format(redditObject.author.name)
                        redditObject.reply(body=response)
                        self.posted.append(num)
                        redditObject.upvote()
                        writeComment(redditObject.id)
                        link = f"{redditObject.author.name}: {to_check}\nResponse: **'{response}'** \nLink - https://www.reddit.com{redditObject.permalink}"
                        self.send_webhook(link)

    def run(self):
        print("Vizzy is online.")
        comment_stream = self.subreddit.stream.comments(pause_after=-1)
        submission_stream = self.subreddit.stream.submissions(pause_after=-1)

        while True:
            for comment in comment_stream:
                if comment is None:
                    break
                else:
                    self.vizzytime(comment, "comment")

            for submission in submission_stream:
                if submission is None:
                    break
                else:
                    self.vizzytime(submission, "post")


vizzy = VIZZY_T()
