from sql import *
from dotenv import load_dotenv
import os
import praw
import json


if not os.path.exists('vizzy_sentient.json'):
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

    # Pull data about comments Vizzy responded to, dump 'em into a dict
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
                if comment_obj.score < temp.score:
                    comment_dict[comment_obj.id] = {
                        "original_points":comment_obj.score,
                        "original_body":comment_obj.body,
                        "vizzy_body":temp.body,
                        "vizzy_points":temp.score
                    }
        except:
            pass


    # Dump to a file
    with open("vizzy_sentient.json","w",encoding="UTF-8") as file:
        data = json.dumps(comment_dict)
        file.write(data)
        file.close()

else:
    # Dump to a file
    with open("vizzy_sentient.json", "r", encoding="UTF-8") as file:
        data = file.read()
        sentient = json.loads(data)
        file.close()

# Parse the sentience out

vizzy_good = {}
vizzy_bad = {}
vizzy_meh = {}
vizzy_best = {}

for comment in sentient.keys():
    try:
        ratio = sentient[comment]['vizzy_points'] / sentient[comment]['original_points']
        if ratio > 1.0:
            vizzy_good[comment] = {
                "original_points":sentient[comment]['original_points'],
                "original_body":sentient[comment]['original_body'],
                "vizzy_body":sentient[comment]['vizzy_body'],
                "vizzy_points":sentient[comment]['vizzy_points'],
                "ratio": ratio
            }
        elif ratio == 1.0:
            vizzy_meh[comment] = {
                "original_points":sentient[comment]['original_points'],
                "original_body":sentient[comment]['original_body'],
                "vizzy_body":sentient[comment]['vizzy_body'],
                "vizzy_points":sentient[comment]['vizzy_points'],
                "ratio": ratio
            }
        elif ratio < 0:
            pass
        else:
            vizzy_bad[comment] = {
                "original_points":sentient[comment]['original_points'],
                "original_body":sentient[comment]['original_body'],
                "vizzy_body":sentient[comment]['vizzy_body'],
                "vizzy_points":sentient[comment]['vizzy_points'],
                "ratio": ratio
            }

        if sentient[comment]['vizzy_points'] > 100:
            vizzy_best[comment] = {
                "original_points":sentient[comment]['original_points'],
                "original_body":sentient[comment]['original_body'],
                "vizzy_body":sentient[comment]['vizzy_body'],
                "vizzy_points":sentient[comment]['vizzy_points'],
                "ratio": ratio
            }
    except:
        pass



# Sort the dictionary by subkey "ratio", inverted so highest ratio is first
for k in sorted(vizzy_good, key=lambda x: vizzy_good[x]['ratio'], reverse=True):
    vizzy_good[k] = vizzy_good.pop(k)

# Dump to a file
with open("vizzy_good.json","w",encoding="UTF-8") as file:
    data = json.dumps(vizzy_good)
    file.write(data)
    file.close()



# Sort the dictionary by subkey "ratio", lowest ratio (Worst comments) is first.
for k in sorted(vizzy_bad, key=lambda x: vizzy_bad[x]['ratio']):
    vizzy_bad[k] = vizzy_bad.pop(k)

# Dump to a file
with open("vizzy_bad.json","w",encoding="UTF-8") as file:
    data = json.dumps(vizzy_bad)
    file.write(data)
    file.close()



# Sort the dictionary by subkey "ratio", lowest ratio (Worst comments) is first.
for k in sorted(vizzy_meh, key=lambda x: vizzy_meh[x]['ratio']):
    vizzy_meh[k] = vizzy_meh.pop(k)

# Dump to a file
with open("vizzy_meh.json","w",encoding="UTF-8") as file:
    data = json.dumps(vizzy_meh)
    file.write(data)
    file.close()



# Sort the dictionary by subkey "ratio", lowest ratio (Worst comments) is first.
for k in sorted(vizzy_best, key=lambda x: vizzy_best[x]['vizzy_points'], reverse=True):
    vizzy_best[k] = vizzy_best.pop(k)

# Dump to a file
with open("vizzy_best.json","w",encoding="UTF-8") as file:
    data = json.dumps(vizzy_best)
    file.write(data)
    file.close()


from fuzzywuzzy import fuzz
from fuzzywuzzy import process


# Dump to a file
with open("vizzy_best.json","r",encoding="UTF-8") as file:
    data = file.read()
    test = json.loads(data)
    file.close()


# This kind of works but not really

comments_test = []
for comment in test:
    comments_test.append(test[comment]['original_body'])


test_dict = {}
for comment in comments_test:
    if test_dict == {}:
        test_dict[comment] = []
    else:
        for key in test_dict.keys():
            if fuzz.token_sort_ratio(key,comment) > 55:
                test_dict[key].append(comment)
                break
        if not comment in test_dict.keys():
            test_dict[comment] = []

for key in test_dict.keys():
    if test_dict[key] == []:
        pass
    else:
        print(f"{key} --- {test_dict[key]}\n\n")