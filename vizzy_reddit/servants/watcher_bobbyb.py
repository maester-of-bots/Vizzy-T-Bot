from dotenv import load_dotenv
import os
import praw
import requests
from sql import *
from time import sleep


# Load in credentials from .env
load_dotenv()

reddit = praw.Reddit(
            client_id=os.getenv('bobby_b-client_id'),
            client_secret=os.getenv('bobby_b-client_secret'),
            password=os.getenv('bobby_b-password'),
            user_agent=os.getenv('bobby_b-user_agent'),
            username=os.getenv('bobby_b-username')
        )



# subreddit = tyrion.subreddit('freefolk+houseofthedragon')

subreddit = reddit.subreddit('freefolk')

webhook="https://discord.com/api/webhooks/1030705508539179139/nbNv5M4SeKj2lY6J34xtTXx7GdbxkNLeU4gOJYyCyWYQEYUnzm82OSGkgdtIaF801wF1"



def checkonlarys():
    comments = reddit.redditor("bobby-b-bot").comments.new()
    base = reddit.comment(id='izdx2n8')
    for comment in comments:
        if comment.created > base.created:
            return True
        else:
            pass
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