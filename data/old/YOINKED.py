'''
# Special quote for some reason
self.final_quote = '"I, Viserys Targaryen, first of his name... King of the Andals, and the Rhoynar, and the First Men, ' \
                   'Lord of the Seven Kingdoms, and Protector of the Realm, do hereby name...' \
                   '{} Princess of Dragonstone and heir to the Iron Throne.'
self.hf = ["IT'S ALRIGHT ANDY! IT'S JUST BOLOGNESE!", "Don't you go bein' a twat now", 'Two blokes and a fuck-load of cutlery!']


if "hot fuzz" in to_check:
    num = randint(0, len(self.hf) - 1)
    response = self.hf[num]
else:
    response = self.quotes[num]

if "{}" in response:
    response = response.format(redditObject.author.name)

redditObject.reply(body=response)
self.posted.append(num)
redditObject.upvote()
writeComment(redditObject.id)
link = f"\n{redditObject.author.name}: {to_check}\nResponse: **'{response}'** \nLink - https://www.reddit.com{redditObject.permalink}"
self.send_webhook(link)
except Exception as e:
print(e)
link = F'ERROR - {e}\nLink - https://www.reddit.com{redditObject.permalink}'
self.send_webhook(link)
elif "the whore is pregnant!" in to_check:
seed()
bobby_b_responses = ['I’ll have your tongue for that!', "GODS BE GOOD!!", "*I WILL HAVE YOUR TONGUE FOR THAT!*",
                     "This is a lie. You have been lied to.", "*There's a boy in the Queen's belly. I know it.*",
                     "*Then he will be loved and cherished.*", ]
num = randint(0, len(bobby_b_responses) - 1)
redditObject.reply(body=bobby_b_responses[num])
writeComment(redditObject.id)
redditObject.upvote()
link = f"\n{redditObject.author.name}: {to_check}\nResponse: **'{bobby_b_responses[num]}'** \nLink - https://www.reddit.com{redditObject.permalink}"
self.send_webhook(link)
elif "you've got a mustache" in to_check:
redditObject.reply(body="**I KNOW**")
writeComment(redditObject.id)
redditObject.upvote()
link = f"\n{redditObject.author.name}: {to_check}\nResponse: **I KNOW** \nLink - https://www.reddit.com{redditObject.permalink}"
self.send_webhook(link)
'''