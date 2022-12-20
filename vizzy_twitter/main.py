
import time
import requests


from quotes import quotes
from utils import *
import random

import discord

from discord import SyncWebhook

def getQuote():
    random.seed()
    x = random.randint(0,len(quotes)-1)
    quote = quotes[x]
    return quote



def craft_embed(title, user_comment, webhook, url, thumbnail, response, color=0x00ff00):


    e = discord.Embed(title=title, description=user_comment,
                      url=url,
                      color=color)

    e = e.add_field(name="Response:", value=response, inline=True)

    e = e.set_thumbnail(url=thumbnail)

    webhook = SyncWebhook.from_url(webhook)

    webhook.send(embed=e)

    return e

def send_webhook(url, body):
    """Use webhooks to notify admin on Discord"""
    data = {'content': body, 'username': 'Vizzy Twitter'}
    requests.post(url, data=data)


def test():
    # calling the api
    api = tweepy.API(auth)

    # the ID of the status
    id = 1272771459249844224

    # fetching the status
    status = api.get_status(id)

    # fetching the text attribute
    text = status.text


def start():
    load_dotenv()
    url = os.getenv('webhook')

    api = make_api()
    while True:
        tweets = tweet_search(api, "Vizzy T", 500, 500)

        for tweet in tweets:
            if str(tweet.id) in getComments() or tweet.user.id == 1587874000553779202:
                print("In DB, skipping.")
                pass
            else:
                quote = getQuote()

                if "{}" in quote:
                    quote = quote.replace("{}",tweet.user.screen_name)

                tweet_url = 'https://twitter.com/twitter/statuses/'+str(tweet.id)

                reply = api.update_status(status=quote, in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True)

                reply_url = 'https://twitter.com/twitter/statuses/'+str(reply.id)

                craft_embed('Vizzy T Twitter Bot', f"{reply_url}\n{tweet.text}", url, tweet_url, 'https://thc-lab.net/ffs/vizzy-t-bot.jpeg', quote)

                writeComment(tweet.id)

                time.sleep(15)

        print("Sleeping for fifteen seconds before searching again.")
        time.sleep(15)

while True:
    start()
