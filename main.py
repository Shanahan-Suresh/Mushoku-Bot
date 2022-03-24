import discord
import os
import requests
import json
import asyncio
import random

token = os.environ['TOKEN']
client = discord.Client()

@client.event
async def on_ready():
  print('Logged In as {0.user}'.format(client))
  activity = discord.Game(name="MT Help", type=3)
  await client.change_presence(status=discord.Status.idle, activity=activity)

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  msg = message.content

  with open("users.json","r") as file:
    users = json.load(file)
    user = message.author
    user_id = str(user.id)
    
    if msg == "MT Points":
      if user_id in users:
        with open("users.json","w") as file:
          users[user_id]["Points"] += 10
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('10 Points Awarded !')
      else:
        with open("users.json","w") as file:
          users = {}
          users[user_id] = {}
          users[user_id]["Points"] = 0
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('Points are tracked')

    if msg == "MT Points Clear":
      with open("users.json","w") as file:
          users[user_id]["Points"] = 0
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('All points cleared')

		

  async def trivia_mode():
    bot_message = ''
    reactions = ["🇦", "🇧", "🇨", "🇩", "🇪"]
    
    questions = {
      'At what age was Rudeus hit by a truck during his previous life ?': 'C', 
      'Ruijerd Superdia is also known as... ?': ['C','E'],
      'Ghyslaine is part of the ___ race.': 'B' }

    choices = [
              ["A. 22","B. 28","C. 34","D. 41"],
              ["A. Demonic Reaper","B. The Evil Supard","C. Dead End","D. Protector of Children", "E. Guard Dog Ruijerd"],
              ["A. Demon","B. Beastfolk","C. Marewolf","D. Forestor"]
              ]

    responses = [
              ["Come on bro, did he look that young ?","Close, but not quite","That's right, you got it !","D. If he was that old, he might've died from a heart attack instead."],
              ["Terrifying, but not right.","Although most people believe he's evil, nobody calls him this.","Correct ! He's known as 'Dead End' because those who meet him will meet their 'dead end'. (or so the rumour goes)","A more accurate name out of all the choices, but sadly, very few people regard him as such.", "Also correct ! He's known as Guard Dog Ruijerd of Dead End during his time partying up with Rudeus and Eris. "],
              ["A demon huh ? Although its true that Ghylaine's race often intermingles closely with the Demon race, she isn't a half-breed. Better luck next round !","Right ! Did you guess that based on her tail and fluffy ears ?","Sorry to say, there is no such race in Mushoku Tensei's world","What even is a 'Forestor' ? Someone who lives in a forest ? I sure don't know."]
              ]
    
    random_number = random.randint(0, len(questions)-1)

    question_keys = list(questions.keys())
    question = question_keys[random_number]
    choice = choices[random_number]
    response = responses[random_number]
    choices_message = '\n'.join(choice)
    correct_answer = questions.get(question)

    embedded = discord.Embed(title = f"{question}\n{choices_message}")
    bot_message = await message.channel.send(embed = embedded)
    for i in range (len(choice)):
        await bot_message.add_reaction(reactions[i])


    answered = False
    def check(reaction, user):
        reacts = ["🇦", "🇧", "🇨", "🇩", "🇪"]
        if user == client.user:
          return
        else:
          return user == message.author and str(reaction.emoji) in reacts
        

    try:
      reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
    except asyncio.TimeoutError:
      await message.channel.send('Timeout, try to react faster next time')
    else:
      #if
      #elif isinstance(correct_answer, list):
      #if  
          if reaction.emoji == "🇦":
              embedded = discord.Embed(title = f"{response[0]}\n")
              await message.channel.send(embed = embedded)
          elif reaction.emoji == "🇧":
              await message.channel.send(response[1])
          elif reaction.emoji == "🇨":
              await message.channel.send(response[2])
          elif reaction.emoji == "🇩":
              await message.channel.send(response[3])
          elif reaction.emoji == "🇪":
              await message.channel.send(response[4])
          else:
              await message.channel.send('What kind of answer is that ?')
        

  if message.content.startswith("MT Trivia"):
    await trivia_mode()

    
        # The following line is optional: it removes the reaction added by the user 
        #await reply.remove_reaction(reaction, user) 
                  
#@client.event
#async def on_reaction_add(reaction, user):
  #await reaction.message.channel.send(f"{user} reacted with {reaction.emoji}")

    

client.run(token)

'''
    def check_answer(reaction, user):
        return user == ctx.author

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check_answer)
            await reply.remove_reaction(reaction, user)

            # Shorter representation of that if-else block.
            if reaction.emoji in emojis:
                print(emojis.index(reaction.emoji) + 1)
                break
            else:
                print("Unknown reaction")

        except asyncio.TimeoutError:
            print("Timeout")'''
