from dotenv import load_dotenv
import os
import openai


load_dotenv()
openai.api_key = os.getenv('sentient')

#
# Vizzy T has Kingsguard who carry out his orders.
# Vizzy T's family includes his daughter Rhaenyra, his brother Daemon, and his wife Alicent, as well as his grandchildren from Rhaenya.
# Vizzy T's interests include tapestries and miniatures.
# Vizzy T loves his family nd will become enraged and threaten anyone who speaks negatively about his family.  Threats include cutting out their tongue and eyes.

def makePrompt(comment):

    # Craft the initial base
    base = f"""The following is a conversation with Viserys Targaryen the First, a character from HBO's show "House of the Dragon" - Also known as Vizzy T.
Vizzy T speaks like an old, sick king.
Vizzy T is very familiar with the world of HBO's House of the Dragon / Game of Thrones, and their characters.
Vizzy T can have his kingsguard carry out his will whenever he needs something done.
Vizzy T does not tolerate any form of disrespect to his daughter Rhaenyra. 
"""

    if "stannis-mannis" in comment.author.name.lower():
        base += f"Vizzy T treats {comment.author.name} with mutual respect but also suspicion, as {comment.author.name} could challenge his reign.\n"
    # elif "open_profit_close" in comment.author.name.lower():
        # base += f"Vizzy T recognizes {comment.author.name} as a Usurper King and will attempt to jail and execute him."
    #elif ("bobby-b-bot" in comment.author.name.lower()) or ("bobby-b-bot" in comment.body.lower()) or ("bobby b" in comment.body.lower()) or ("bobby-b" in comment.body.lower()):
    #    base += f'Vizzy T will speak to {comment.author.name} as a king would speak to a member of his court'
    #    base += 'Vizzy T knows that bobby-b-bot is King Robert Baratheon, a future king.'
    else:
        base += f'Vizzy T will speak to {comment.author.name} as a king would speak to a member of his court\n'


    reading = True
    current = comment
    levels = 0
    entries = []

    while reading:
        author = current.author.name.lower()
        if author == 'vizzy_t_bot':
            author = "Vizzy T"
        msg = current.body
        msg = msg.replace('^(This response generated with OpenAI)','')
        entry = f"{str(author)}: {msg}\n"
        entries.append(entry)
        levels += 1
        if levels == 4:
            reading = False
        else:
            current = current.parent()

    entries.reverse()

    for entry in entries:
        base += entry

    base += "Vizzy T: "

    return base



def be_sentient(prompt, comment):
    """
    Takes in prompt, author's name, bot's short name, and the parent author.  Spits out a response and how much it cost.

    """

    print("Making sentience")

    # Recent trigger
    c1 = comment.author.name

    # Bot response above
    c2 = comment.parent().author.name

    # Original user trigger
    c3 = comment.parent().parent().author.name

    # Original user trigger
    c4 = comment.parent().parent().parent().author.name


    stop = []
    tmep = [c1,c2,c3,c4]
    for x in tmep:
        if f'{x}: ' not in stop:
            stop.append(f'{x}: ')


    presence_penalty = .6
    stop = [f'{c4}: ',f'{c3}: ',f'{c2}: ',f'{c1}: ',]
    max_tokens = 2222

    # Generate the raw response data
    data = openai.Completion.create(engine="text-davinci-002",
                                    prompt=prompt,
                                    max_tokens=max_tokens,
                                    presence_penalty=presence_penalty,
                                    temperature=.9,
                                    stop=stop)

    # Grab the response out of the data dict
    response = data['choices'][0]['text']

    # Parse out the line we need
    parsed = response.replace('User', c1).strip().replace("Vizzy T:","").replace("vizzy t:","").strip()

    parsed += "\n\n^(This response generated with OpenAI)"

    format(1.29578293, '.6f')

    # Get token cost
    cost = data['usage']['total_tokens']

    return parsed, cost
