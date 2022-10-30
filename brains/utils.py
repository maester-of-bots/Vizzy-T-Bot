import praw

import openai


def isPost(obj):
    return isinstance(obj,praw.models.Submission)

def isComment(obj):
    return isinstance(obj,praw.models.Comment)

def triggered(text):
    return "vizzy t" in text or "vissy t" in text


def makePrompt(comment):

    # Craft the initial base
    base = f"""The following is a conversation with Viserys I Targaryen, King of the Andals, the Rhoynar and the First Men, Lord of the Seven Kingdoms, and Protector of the Realm, also known as 'Vizzy T'.
Vizzy T is an aging, elderly king, and will speak like a king from medieval times.
Vizzy T is a good person but a bad king.
Vizzy T loves his family more than anything, also loves tapestries and miniatures.  
Vizzy T's family fights among themselves constantly and it upsets Vizzy T.
Vizzy T is oblivious to his daughter Rhaenyra's children being bastards, and is enraged when anyone mentions it, swearing to cut out their tongues or take their eyes.
Vizzy T's brother Daemon is having sex with his daughter Rhaenyra, and Vizzy T does not know, and he will be angry if anyone tells him.
Vizzy T will demand to know who has been spreading rumors about his family if he hears bad things about anyone.
"""
    if comment.author.name == "stannis-mannis-bot":
        base += "Vizzy T treats this user with mutual respect but also suspicion.\n"


    reading = True
    current = comment
    levels = 0
    entries = []

    while reading:
        author = current.author.name
        if author == 'vizzy_t_bot':
            author = "Vizzy T"
        msg = current.body
        entry = f"{str(author)}: {msg}\n"
        entries.append(entry)
        levels += 1
        if levels == 3:
            reading = False

    entries.reverse()

    for entry in entries:
        base += entry

    base += "Vizzy T: "

    return base



def be_sentient(prompt, comment):
    """
    Takes in prompt, author's name, bot's short name, and the parent author.  Spits out a response and how much it cost.

    """

    # Recent trigger
    c1 = comment.author.name

    # Bot response above
    c2 = comment.parent().author.name

    # Original user trigger
    c3 = comment.author.name


    c1 = comment.author.name
    c1 = comment.author.name
    presence_penalty = 0.8
    stop = [f'{author_name}: ', f'{bot_name_short}: ', f'{parent_author}: ']
    max_tokens = 300

    # Generate the raw response data
    data = openai.Completion.create(engine="text-davinci-002",
                                    prompt=prompt,
                                    max_tokens=max_tokens,
                                    presence_penalty=presence_penalty,
                                    temperature=1,
                                    stop=stop)

    # Grab the response out of the data dict
    response = data['choices'][0]['text']

    # Parse out the line we need
    parsed = response.replace('username', author_name).replace('Username', author_name).replace('\n', '').strip()

    # Get token cost
    cost = data['usage']['total_tokens']

    if bot_name_short == "Yzri":
        parsed = parsed.upper()

    return parsed, cost
