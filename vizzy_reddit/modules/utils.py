from sentience import *

import praw
import discord
from discord import SyncWebhook
from datetime import *
import socket
from dotenv import load_dotenv
import os
import json




def get_ip():
    return requests.get('https://ipv4.canhazip.com').text.strip()


def resolve_name(name):
    results = socket.gethostbyname_ex(name)
    ips = []
    for thing in results:
        if thing == []:
            check = "thc"
        elif type(thing) == list:
            check = thing[0]
        elif type(thing) == str:
            check = thing
        else:
            check = "thc"
        if "thc" in check:
            pass
        else:
            ips.append(check)
    return ips[0]


def is_production():

    ip = get_ip()

    print(ip)

    if ip == resolve_name('thc-lab.net'):

        print("We are in production")

        return True

    else:

        print("We are in Test")

        return False



class webhookmaster:
    def __init__(self):

        load_dotenv()

        self.webhooks = {
            'vizzy-test':os.getenv('vizzy-test'),
            'vizzy-canon':os.getenv('vizzy-canon'),
            'vizzy-sentient':os.getenv('vizzy-sentient'),
            'tyrion-dwarfbot':os.getenv('tyrion-webhook'),
            'bobby_b':os.getenv('bobby_b-webhook'),
            'bofh':os.getenv('bofh-webhook'),
            'spam':os.getenv('spam'),

        }



    def craft_embed(self,
                    description,
                    url,
                    author,
                    comment,
                    response,
                    bot='vizzy-canon',
                    color=0x00ff00,
                    title="Vizzy T Notification",
                    thumb='https://thc-lab.net/ffs/vizzy-t-bot.jpeg'):

        if "sentient" in description:
            bot = "vizzy-sentient"
            color = 0xFF0000

        webhook = self.webhooks[bot]

        e = discord.Embed(title=title, description=description, url=url, color=color)

        e = e.add_field(name=author, value=comment, inline=True)

        if bot == "bofh":
            pass
        else:
            e = e.add_field(name="Vizzy T:", value=response, inline=True)

        e = e.set_thumbnail(url=thumb)

        webhook = SyncWebhook.from_url(webhook)

        webhook.send(embed=e)


    def send_errors(self, e, url, comment=None):
        """Use webhooks to notify admin on Discord"""

        title = 'Vizzy T Error Notification'

        author = "Bastard Operator from Hell"

        color = 0xff0000

        if "object has no attribute 'name" in str(e):
            pass
        else:
            self.craft_embed(title, url=url, author=author, comment=e,response="Dummy field.", bot='bofh', color=color)






def makeBots():
    bots = {}

    for dir in os.listdir('bots'):
        file = os.path.join('bots', dir, f"{dir}.json")
        with open(file,'r') as lines:
            char_lines = lines.read()
            data = json.loads(char_lines)

        bots[dir] = data

    load_dotenv()

    for bot in bots.keys():

        print(f"Loading {bot}")
        bots[bot]['r'] = praw.Reddit(
            client_id=os.getenv(bots[bot]['envs'][0]),
            client_secret=os.getenv(bots[bot]['envs'][1]),
            password=os.getenv(bots[bot]['envs'][2]),
            user_agent=os.getenv(bots[bot]['envs'][3]),
            username=os.getenv(bots[bot]['envs'][4])
        )

        base = bots[bot]['envs'][0].split('-')[0]
        wh = f"{base}-webhook"
        bots[bot]['webhook'] = os.getenv(wh)

    return bots


def checkStatus(bots):
    r = bots['vizzy_t_bot']['r']
    for bot in bots.keys():
        bot_obj = r.redditor(bot)
        if hasattr(bot_obj,'is_suspended'):
            print(f"{bot_obj.user.me()} is currently suspended.")
        else:
            print(f"{bot_obj.user.me()} is fine.")






def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results


def isPost(obj):
    return isinstance(obj,praw.models.Submission)

def isComment(obj):
    return isinstance(obj,praw.models.Comment)

def triggered(text):
    return "vizzy t" in text or "vissy t" in text


def checkTime(obj):
    time = obj.created
    timestamp = datetime.fromtimestamp(time)
    # print(timestamp)
    if (datetime.now() - timedelta(hours=7)) < timestamp:
        return True
    else:
        # print("Skipping .old comment.")
        return False


