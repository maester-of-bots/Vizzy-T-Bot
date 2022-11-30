from utils import *

import discord

from discord import SyncWebhook

from dotenv import load_dotenv
import os

load_dotenv()
spam_webhook = os.getenv('spam_webhook')

def craft_embed(repost_url, response, color=0x00ff00):

    found = "\n".join(response)

    e = discord.Embed(title="Repost Detected", description=repost_url,
                      url=repost_url,
                      color=color)

    e = e.add_field(name="Original:", value=found, inline=True)

    webhook = SyncWebhook.from_url(spam_webhook)

    webhook.send(embed=e)

    return e


load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv('vizzy_client_id'),
    client_secret=os.getenv('vizzy_client_secret'),
    password=os.getenv('vizzy_password'),
    user_agent=os.getenv('vizzy_user_agent'),
    username=os.getenv('vizzy_username')
)

# Set the subreddit to monitor
subreddit = reddit.subreddit('freefolk')

for post in subreddit.stream.submissions(skip_existing=True):
    query = post.title

    seen = []

    for exPost in subreddit.search(query):
        if exPost.title == query and exPost.id != post.id:
            seen.append(f'https://www.reddit.com{exPost.permalink}')

    if seen:
        data = craft_embed(f'https://www.reddit.com{post.permalink}', seen)
