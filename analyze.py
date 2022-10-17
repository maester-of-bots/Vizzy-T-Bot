from sql import *
from dotenv import load_dotenv
import os
import praw

# Load in credentials from .env
load_dotenv()

# Set the bot's username
bot_username = os.getenv('reddit_username')

webhook_url = os.getenv('webhook')

# Initialize a Reddit object
reddit = praw.Reddit(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    password=os.getenv('password'),
    user_agent=os.getenv('user_agent'),
    username=bot_username
)


comments = getComments()
comment_dict = {}

for comment in comments:
    try:
        comment_obj = reddit.comment(id=comment)
        comment_obj.refresh()
        temp = None
        for reply in comment_obj.replies:
            if reply.author == "vizzy_t_bot":
                temp = reply
                break
        if temp:
            comment_dict[comment_obj] = {
                "original_points":comment_obj.score,
                "original_body":comment_obj.body,
                "vizzy_body":temp.body,
                "vizzy_points":temp.score
            }
    except:
        pass
