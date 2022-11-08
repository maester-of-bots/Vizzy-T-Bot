
import time
import requests


from quotes import quotes
from utils import *
import random


def getQuote():
    random.seed()
    x = random.randint(0,len(quotes)-1)
    quote = quotes[x]
    return quote


def send_webhook(url, body):
    """Use webhooks to notify admin on Discord"""
    data = {'content': body, 'username': 'Vizzy Twitter'}
    requests.post(url, data=data)

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

                print('https://twitter.com/twitter/statuses/'+str(tweet.id))

                reply = api.update_status(status=quote, in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True)

                reply_url = 'https://twitter.com/twitter/statuses/'+str(reply.id)

                send_webhook(url, reply_url)

                writeComment(tweet.id)

                time.sleep(15)

        print("Sleeping for fifteen seconds before searching again.")
        time.sleep(15)

while True:
    start()
