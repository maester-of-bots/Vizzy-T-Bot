from dotenv import load_dotenv
import os
import praw
import requests
from utils import submissions_and_comments
from sql import *
from time import sleep


# Load in credentials from .env
load_dotenv()


# Initialize a Reddit object
tyrion = praw.Reddit(
    client_id=os.getenv('tyrion_client_id'),
    client_secret=os.getenv('tyrion_client_secret'),
    password=os.getenv('tyrion_password'),
    user_agent=os.getenv('tyrion_user_agent'),
    username=os.getenv('tyrion_username')
)



# subreddit = tyrion.subreddit('freefolk+houseofthedragon')
subreddit = tyrion.subreddit('vizzy_t_test')
subreddit = tyrion.subreddit('freefolk')

webhook="https://discord.com/api/webhooks/1030705508539179139/nbNv5M4SeKj2lY6J34xtTXx7GdbxkNLeU4gOJYyCyWYQEYUnzm82OSGkgdtIaF801wF1"



def checkonlarys():
    comments = tyrion.redditor("larys-strong-bot").comments.new()
    base = tyrion.comment(id='iuw5m6g')
    for comment in comments:
        if comment.created > base.created:
            return True

    return False


def send_webhook(body):
    data = {'content': body, 'username': 'Sentient Tyrion'}
    requests.post(webhook, data=data)

def run():

    for comment in subreddit.stream.comments():
        try:
            if "tyrion-dwarfbot" in str(comment.author).lower():
                pass

            elif "feet" in str(comment.body.lower()):

                if str(comment.id) in getCommentsdwarf():
                    pass

                else:

                    ourBotHasReturned = checkonlarys()

                    if ourBotHasReturned:
                        send_webhook("LORD STRONG HAS RETURNED!!  https://www.reddit.com" + comment.permalink)
                        comment.reply(body="MY LORD FEETBOT RETURNS!")
                        writeDwarfComment(comment.id)
                        return 0
                    else:
                        sleep(10)

                        comment.refresh()
                        comment.replies.replace_more()
                        child_comments = comment.replies.list()

                        should_comment = True
                        for c in child_comments:
                            if "( ͡° ͜ʖ ͡°)" in c:
                                writeDwarfComment(c.id)
                                should_comment = False

                        if should_comment and not checkonlarys():
                            response = """>feet \n\n\n\n*...sigh...*\n\n\n\n( ͡° ͜ʖ ͡°)"""
                            comment.reply(body=response)
                            writeDwarfComment(comment.id)
                            body = f"Feetbot Standin:\nhttps://www.reddit.com{comment.permalink})"
                            send_webhook(body)
                        else:
                            print(f"Skipping https://www.reddit.com{comment.permalink}")
        except:
            pass





run()