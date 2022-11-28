from dotenv import load_dotenv
import logging
import os
from sql import *

logger = logging.getLogger()

import tweepy


def get_creds():
    load_dotenv()
    key = os.getenv('key')
    secret = os.getenv('secret')
    token = os.getenv('token')
    token_secret = os.getenv('token_secret')
    return [key,secret,token,token_secret]

def make_api():
    secret = get_creds()
    auth = tweepy.OAuthHandler(secret[0], secret[1])
    auth.set_access_token(secret[2], secret[3])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    try:
        api.verify_credentials()
        print("credentials verified")
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        print("error verifying credentials")
        raise e
    logger.info("API created")
    return api



def postTweet(api, content):
    tweet = api.update_status(content)
    return tweet

def tweet_search(api,query,max,count2):
    q = f'"{query}" AND -filter:retweets AND -filter:replies&result_type=recent'
    tweets = [tweet for tweet in tweepy.Cursor(api.search_tweets, q=q, lang='en', result_type="mixed",count=max).items(count2)]
    elon =  api.user_timeline(screen_name='elonmusk', count=3, include_rts = False)

    full = tweets + elon
    return full



def elon_search(api):



class ConnectionTester(tweepy.Stream):
    def on_connection_error(self):
        self.disconnect()

