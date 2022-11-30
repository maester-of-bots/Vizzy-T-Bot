from dotenv import load_dotenv
import os
import openai
import praw

import requests

from datetime import *

load_dotenv()
openai.api_key = os.getenv('sentient_v')

# Fastest

openai_models = {
    "ada": {
        "1000": 0.0004,
        "1": 0.0004/1000,
        "name": 'text-ada-001'
    },
    "babbage": {
        "1000": 0.0005,
        "1": 0.0005/1000,
        "name": 'text-babbage-001'
    },
    "curie": {
        "1000": 0.0020,
        "1": 0.0020/1000,
        "name": 'text-curie-001'
    },
    "davinci": {
        "1000": 0.0200,
        "1": 0.0200/1000,
        "name": 'text-davinci-002'
    },
}

def isComment(obj):
    return isinstance(obj,praw.models.Comment)


def tokenCalculator(comment, model):
    """ Return the amount of tokens this comment would represent"""
    spaces = comment.count(' ')
    words = len(comment)
    chars = words - spaces
    tokens = chars / 4

    # Dollar amounts
    costs = {
        "ada": tokens * openai_models["ada"]["1"],
        "babbage": tokens * openai_models["babbage"]["1"],
        "curie": tokens * openai_models["curie"]["1"],
        "davinci": tokens * openai_models["davinci"]["1"],
    }

    return tokens, costs[model]


def WOULDYOULIKETOSEETHETAPESTRIES(prompt):
    full_prompt = f"Regal tapestries adorned with {prompt}"
    image_resp = openai.Image.create(prompt=full_prompt, n=1, size='1024x1024')

    url = image_resp['data'][0]['url']

    submit_url = 'https://thc-lab.net/art.html'

    timestamp = datetime.now().timestamp()

    filename = f"Tapestries_{timestamp}.jpeg"

    payload = {
        'code': 'fuck you you fucking fuck',
        'url': url,
        'filename': filename
    }

    r = requests.post(submit_url, data=payload)
    return r.text


def get_sentient(comment):

    # Craft the initial base
    base = f"""The following is a conversation with Viserys Targaryen the First, a character from HBO's show "House of the Dragon" - Also known as Vizzy T.
Vizzy T speaks like an old, sick king who has just awoken from a long slumber.
"""

    if not "bobby-b-bot" in comment.author.name.lower():
        base += f'Vizzy T will speak to {comment.author.name} as a king would speak to a member of his court, and commands respect from them.\n'
    else:
        base += "Vizzy T recognizes bobby-b-bot as King Robert Baratheon, a future King of Westeros."


    reading = True
    current = comment
    levels = 0
    entries = []

    # total_count = 0

    stop = []


    while reading:
        try:
            author = current.author.name.lower()
            if author == 'vizzy_t_bot':
                author = "Vizzy T"

            if f'{author}: ' not in stop:
                stop.append(f'{author}: ')

            try:
                msg = current.body.replace('^(This response generated with OpenAI) [DaVinci]','')
            except:
                reading = False


            # Don't read past a comment that's 500 tokens or more
            # tokens, costs = tokenCalculator(msg )

            # if tokens > 500 or total_count > 1000:
            #    reading = False
            # else:
            #    total_count += tokens

            entry = f"{str(author)}: {msg}\n"
            entries.append(entry)

            levels += 1

            if levels == 4:
                reading = False
            else:
                try:
                    current = current.parent()
                    if isComment(current):
                        continue
                    else:
                        reading = False
                except:
                    reading = False
        except:
            reading = False

    # addition = .1 * len(entries)

    entries.reverse()

    for entry in entries:
        base += entry

    base += "Vizzy T: "

    print("Making sentience")

    presence_penalty = .8
    max_tokens = 1750

    # Generate the raw response data
    data = openai.Completion.create(engine='text-davinci-002',
                                    prompt=base,
                                    max_tokens=max_tokens,
                                    presence_penalty=presence_penalty,
                                    temperature=.9,
                                    stop=stop)

    # Grab the response out of the data dict
    response = data['choices'][0]['text']

    # Parse out the line we need
    parsed = response.replace('User', comment.author.name).strip().replace("Vizzy T:","").replace("vizzy t:","").strip()

    try:
        if str(comment.parent().body) == parsed:
            return False, False
        else:
            # Get token cost, and round it to six places.
            cost = data['usage']['total_tokens']

            return parsed, cost
    except:
        print("Ugh")
        # Get token cost, and round it to six places.
        cost = data['usage']['total_tokens']

        return parsed, cost



def whore():
    # Craft the initial base
    base = f"""The following is a conversation with Viserys Targaryen the First, a character from HBO's show "House of the Dragon" - Also known as Vizzy T.
    Vizzy T speaks like an old king.
    Vizzy T does not tolerate any form of disrespect towards his daughter. 
    Vizzy T recognizes bobby-b-bot as King Robert Baratheon
    bobby-b-bot:  THE WHORE IS PREGNANT!
    Vizzy T: 
    """

    data = openai.Completion.create(engine='text-davinci-002',
                                    prompt=base,
                                    max_tokens=2000,
                                    presence_penalty=1,
                                    temperature=.9,
                                    stop=['bobby-b-bot: ','Vizzy T: '])

    # Grab the response out of the data dict
    response = data['choices'][0]['text']

    # Parse out the line we need
    parsed = response.replace('User', "Bobby  B").strip().replace("Vizzy T:", "").replace("vizzy t:","").strip()

    parsed += f"\n\n^(This response generated with OpenAI [DaVinci])"

    return parsed
