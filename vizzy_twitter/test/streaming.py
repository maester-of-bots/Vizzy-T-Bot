import time

from utils import *



def doStream():
    load_dotenv()
    bearer = os.getenv('bearer')
    run_stream(make_stream(bearer))


def make_stream(bearer):
    streaming_client = tweepy.StreamingClient(bearer)
    streaming_client.add_rules(tweepy.StreamRule('(Vizzy T) lang:en'))
    # streaming_client.on_response = on_response
    return streaming_client

def on_response(response: tweepy.StreamResponse):
    print("Twat")
    tweet: tweepy.Tweet = response.data
    users: list = response.includes.get("users")
    if "Vizzy T" in tweet.text:
        author_username = users and users[0].username
        print(tweet.text, author_username)
    else:
        print("Skipping tweet")
        pass

def on_error(error: tweepy.errors):
    print(error)

def run_stream(stream):
    stream.filter()
    print("Sleeping")
    time.sleep(2)
    print("Disconnecting")
    stream.disconnect()
