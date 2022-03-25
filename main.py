import discord
import os
import requests
import json
import asyncio
import random

#token and verification
token = os.environ['TOKEN']
client = discord.Client()

#bot startup
@client.event
async def on_ready():
  print('Logged In as {0.user}'.format(client))
  
  #set activity status
  activity = discord.Game(name="MT Help", type=3)
  await client.change_presence(status=discord.Status.idle, activity=activity)

#listens to messages sent by users
@client.event
async def on_message(message):
  
  #ignored if sent by self
  if message.author == client.user:
    return
    
  msg = message.content

  #opens list of users who have set up points
  with open("users.json","r") as file:
    users = json.load(file)
    user = message.author
    user_id = str(user.id)
    
    if msg == "MT Points":

      #print user's current points
      #Idea- rankup only during points check maybe (play fanfare)
      if user_id in users:
        with open("users.json","r") as file:
          user_points = users[user_id]["Points"]
          rank = rank_check(user_points)
          await message.channel.send("{}'s Adventurer Log\n-------------------------------\nMT Points ({})\nRank - {}".format(user.mention, user_points, rank))

      #track new user
      else:
        with open("users.json","w") as file:
          users = {}
          users[user_id] = {}
          users[user_id]["Points"] = 0
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('New adventurer detected ! \nWelcome {}! Your points are now being tracked'.format(user.mention))

    #clear all points
    if msg == "MT Points Clear":
      with open("users.json","w") as file:
          users[user_id]["Points"] = 0
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('All points cleared')

		

  #trivia game mode
  async def trivia_mode():
    bot_message = ''
    reactions = ["🇦", "🇧", "🇨", "🇩", "🇪"]

    #question bank
    questions = {
      'At what age was Rudeus hit by a truck during his previous life ?': 'C', 
      'Ruijerd Superdia is also known as... ?': ['C','E'],
      'Ghyslaine is part of the ___ race.': 'B',
      'How old was Roxy when she first met Rudeus ?': 'C',
      'Lilia first met Paul...': 'A',
      'Sylphy is a(n)...? ': ['C','D'],
      'Ruijerd Superdia had lived through and served in all 4 Human-Demon Wars throughout time. ': 'B',
      'Rudeus could use ___-ranked water magic at the age of 5.': 'C',
      'The three famous Sword Styles are : ': 'A',
    'Pax Shirone is the ___ prince of Shirone.': 'D',
    'The strongest nation in the world is the...': 'A',
    'There are 7 main races in the world of Mushoku Tensei.\nThey are the "Human Race", "Demon Race", "Dragon Race", "Void Race" and what other 3 races ?' : 'C',
    "What's Eris's middle name ? (Eris ___ Greyrat)": ['B','E']}

    #choices correspond to questions.keys()
    choices = [
              ["A. 22","B. 28","C. 34","D. 41"],
              ["A. Demonic Reaper","B. The Evil Supard","C. Dead End","D. Protector of Children", "E. Guard Dog Ruijerd"],
              ["A. Demon","B. Beastfolk","C. Marewolf","D. Forestor"],
              ["A. 18","B. 28","C. 37","D. 128"],
              ["A. during their childhood","B. during Paul's adventuring days","C. after Paul married Zenith","D. shortly before Rudeus was born"],
              ["A. human","B. demon","C. half-elf","D. half-elf, quarter human and quarter beastfolk", "E. half-beastfolk, half-demon"],
              ["A. True","B. False"],
              ["A. Intermediate","B. Advanced", "C. Saint", "D. King", "E. Emperor"],
              ["A. Water God Style, Sword God Style, North God Style","B. Fire Style, Sword Style, Water Style", "C. Sword God Style, Dragon God Style, Demon God Style"],
              ["A. 1st","B. 3rd","C. 4th","D. 7th"],
              ["A. Asura Kingdom","B. Holy Milis Kingdom","C. Kingdom of the Dragon King","D. Three Magic Nation Alliance "],  
              ["A. Beastfolk, Monsters, Gods","B. Elves Race, Dwarfs Race and Beastfolk","C. Seafolk, Sky Race (Angles) and Beastfolk"],
              ["A. Notos","B. Boreas","C. Euros", "D. Zephyrus", "E. (No Middle Name)"]
              ]

    #responses correspond to choices
    responses = [
              ["Come on bro, did he look that young ?","Close, but not quite","That's right, you got it !","If he was that old, he might've died from a heart attack instead."],
              ["Terrifying, but not right.","Although most people believe he's evil, nobody calls him this.","Correct ! He's known as 'Dead End' because those who meet him have their fates cut short (i.e reach a dead end in thier lives) , or so the rumour goes.","A more accurate name out of all the choices.\nSadly, very few people regard him as such.", "Also correct ! He's known as Guard Dog Ruijerd of Dead End during his time partying up with Rudeus and Eris. "],
              ["A demon huh ? Although its true that Ghylaine's race often intermingles closely with the Demon race, she isn't a half-breed. Better luck next round !","Right ! Did her tail and fluffy ears give it away ?","Sorry to say, there is no such race in Mushoku Tensei's world","What even is a 'Forestor' ? Someone who lives in a forest ? I sure don't know."],
              ["A Migurd's body stops aging during their teen years, so I can see why you would think that.","Roxy first left her home and became an adventurer around this periord of her life. It will be some time before she eventually meets Rudeus.","Fun fact: Roxy and Rudeus are both mentally the same age !","Well... she would look the same even if she was this old. Good guess ?"],
              ["Lilia was the daughter of the sword master in the dojo where Pual first picked up swordsmanship. They parted ways after Paul bedded her and ran away from the dojo.","While Paul was living the life of an adventurer, Lilia was serving within the Asura Capital's palace as a royal handmaiden. They did not meet each other during this period of their lives.","Paul and Zenith retired from adventuring after getting married. At this point, they could handle themselves quite well and did not need to hire a maid.","Lilia left her service within the Asuran Palace due to an injury during an assasination attempt on the newborn princess. She was then hired by Paul shortly before Rudeus was born to take care of Zenith's home duties while she was expecting. However, this was not their first meeting."],
            ["Although Sylphy does have human blood running within her, it wouldn't be accurate to call her one as most of her characteristics originate from another heritage.","Her green hair may give off the impression that she's a demon. But she has no demon heritage. The cause of the green hair is instead because of....||the 'Laplace Factor'||","Technically correct ! Her father is half elf, half human, while her mom is a mix of human and beastfolk.","Absolutely right ! Her father is half elf, half human, while her mom is a mix of human and beastfolk. You sure know your stuff !", "A mixed person borne from these 2 races is very common, but Sylphy isn't one of them."],
          ["Ruijerd is pretty old, but the first Human-Demon War took place ~10,000 years ago. An average Supard lives for 500~1000 years, so Ruijerd likely wasn't even born during that period.","Correct ! Ruijerd has only been confirmed to serve during the 4th Human-Demon War (aka Laplace's War). He was one of the most important figures during the war, his efforts shaping the current landscape of the world."],
        ["When he first started learning magic at the age of 2, Rudeus quickly blew past the intermediate stage for almost all schools of magic because of his innate understanding of physics and science.","The magic spells Rudeus used at the age of 3~4 were of this tier. Most of his other schools of magic remain at this tier way long pass his days adventuring in the Demon Continent.", "That's right. Rudeus reached Saint tier at the age of 5. For reference, the most esteemed professors of the best magic university in the world stuggle for most of their lives to reach this rank. It's also why almost no way except those that are close to Rudeus believes this accomplishment.", "Reaching King-ranked magic would engrave you solidly within the history books. It may take some more time before Rudeus can reach this level, but he definitely has the potential ! ", "Emperor-tier magic is found far and few within even the entire history of the world. Currently the number of people capable of even using such powerful magic are countable on a single hand."],
        ["All three of these sword styles were founded by their respective gods centuries ago. Currently, the Sword God Style is the most popular of the three.","Were you thinking of another series ?", "Neither the Dragon God nor the Demon God uses a weapon (they don't need one), and they definitely don't have a sword style under their name."],
      ["The first prince was 32-years old when Rudeus entered Shirone, definitely couldn't be a brat like Pax !","The third prince is the chad Zanoba. Wayyy better than Pax.","The 4th prince had his head ripped apart by Zanoba shortly after he was born (by accident of course !). Too bad it wasn't Pax instead....","Right. Pax is nearly last in line for ascending the throne of the Shirone kingdom.... hopefully he never does !"],
      ["As one of the two sole surviving human nations emerging victorious from Laplace's War, Asura kingdom is rich in both economic and military might, making it the world's strongest superpower nation. Unfortunately, with no threats from the outside, the Asuran royalty and Asuran nobles have been infighting for the last few decades, leaving a good chance for other nations to overtake Asura.","As one of the two sole surviving human nations emerging victorious from Laplace's War , the Holy Milis Kingdom is strong in terms of holy magic and military might. Unfortunately, their isolation with the surrounding demonic kingdoms and distance from other human nations makes their economy fall short.","The Kingdom of the Dragon King is a fast growing nation, recently subjugating many nearby smaller nations. Though they still don't have nearly enough military might to take on great nations like Asura or Holy Milis, frailer nations such as Shirone fall within the threat of their blades.","In terms of magic prowess, the Three Magic Nation Alliance are definitely the pinacle of the world. Though, their efforts are mainly directed towards the progression of magical advancements within society, which leaves them little concern with political or military issues."],
      ["Monsters aren't a race, do you consider animals a race ? And 'Gods' are ranks or titles, they aren't a seperate group of races.","Both elves and dwarfs fall under the category of Beastfolk. This is because the proximity of beastfolk and demon races across hundreds of centuries have led to a variety of new sub-races, which include elves(mainly beastfolk), dwarfs(mainly beastfolk), ogres(mainly demon race), etc.","You got it right ! Both mermaids and angels exist in Mushoku Tensei's world, though it's not likely you'll see any characters from these two races anytime soon (they're VERY seclutive !)."],
      ["Maybe in another timeline......","Right ! Eris is from a branch of the Boreas family, she has 2 older brothers in the royal capital belonging to the main branch. They were sent there to avoid potential uprisings to the main family from a branch family like Eris's.\nGosh, it's pretty complicated.","Euros is one of the 4 noble Greyrat branches, but not Eris's branch.", "Zephyrus is one of the 4 noble Greyrat branches, but not Eris's branch.", "Well... that's true at some point.\nBut I'm sure you knew that, so it's not a spoiler. Right ?"]
              
              ]
    
    random_number = random.randint(0, len(questions)-1)

    question_keys = list(questions.keys())
    question = question_keys[random_number]
    choice = choices[random_number]
    response = responses[random_number]
    choices_message = '\n'.join(choice)
    correct_answer = questions.get(question)

    #send question as an embed
    embedded = discord.Embed(title = f"{question}\n{choices_message}")
    bot_message = await message.channel.send(embed = embedded)
    for i in range (len(choice)):
        await bot_message.add_reaction(reactions[i])


    #answered = False
      
    #Check and return reaction user and all available reactions
    def check(reaction, user):
        reacts = ["🇦", "🇧", "🇨", "🇩", "🇪"]
        if user == client.user:
          return
        else:
          return user == message.author and str(reaction.emoji) in reacts
        

    try:
      reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
    
      #Stop round if time limit exceeded
    except asyncio.TimeoutError:
      await message.channel.send('Timeout, try to react faster next time')

    #carry on if reaction given
    else:   
          channel = message.channel
      
          if reaction.emoji == "🇦":
              flag = check_answer(correct_answer, 'A')
              await create_embed_response(flag, response[0], channel)
            
          elif reaction.emoji == "🇧":
              flag = check_answer(correct_answer, 'B')
              await create_embed_response(flag, response[1], channel)
            
          elif reaction.emoji == "🇨":
              flag = check_answer(correct_answer, 'C')
              await create_embed_response(flag, response[2], channel)
            
          elif reaction.emoji == "🇩":
              flag = check_answer(correct_answer, 'D')
              await create_embed_response(flag, response[3], channel)
            
          elif reaction.emoji == "🇪":
              flag = check_answer(correct_answer, 'E')
              await create_embed_response(flag, response[4], channel)
            
          else:
              await message.channel.send('What kind of answer is that ?')

          if flag == True :
            async def add_points(user):
              with open("users.json","r") as file:
                users = json.load(file)
                
                user_id = str(user.id)
                
              #adds points to existing user
              if user_id in users:
                with open("users.json","w") as file:
                  users[user_id]["Points"] += 10
                  json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
                  
                  
              #create record and then add points to new user
              else:
                with open("users.json","w") as file:
                  users = {}
                  users[user_id] = {}
                  users[user_id]["Points"] = 10
                  json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
                  await message.channel.send('New adventurer detected ! \nWelcome {}! Your points are now being tracked'.format(user.mention))
                             
            await add_points(user)
        


  if message.content.startswith("MT Trivia"):
    await trivia_mode()

  if message.content.startswith("MT Help"):
    channel = message.channel
    await display_embed(channel)

#Function to display help menu (written in notepad, indents may cause issues)
async def display_embed(channel):
	embed = discord.Embed(
		title = 'Available Commands',
		description = 'Ver 0.1 - Trivia mode and point system ',
		colour = discord.Colour.orange()
	)

	embed.set_footer(text='In development v0.1')
	embed.set_image(url='https://media.discordapp.net/attachments/905934829659496458/920654143721467944/Mushoku_Tensei_Isekai_Ittara_Honki_Dasu_Logo_Japones.png')
	file = discord.File("thumbnail2.png")
	embed.set_thumbnail(url="attachment://thumbnail2.png")
	embed.set_author(name = 'MushokuBot Help', icon_url='https://cdn.discordapp.com/attachments/905934829659496458/920656680830791740/286158_-_Copy.jpg')
	embed.add_field(name=':scroll: MT Trivia', value = 'Start a round of Mushoku Tensei trivia !\n(single-player only)', inline = True)
	embed.add_field(name=':diamond_shape_with_a_dot_inside: MT Points', value = 'View your current MT points', inline = True)
	embed.add_field(name=':grey_question: MT Help', value = 'View all available commands', inline = False)
	
	await channel.send(file = file, embed=embed)

#Function to determine user rank based on points
def rank_check(user_points):
  if user_points >= 10000:
    rank = 'God-level Mushoku Ultra Fan'
  elif user_points >= 4500:
    rank = 'Emperor-Tier Mushoku Fan'
  elif user_points >= 2000:
    rank = 'King-Tier Mushoku Fan'
  elif user_points >= 1400:
    rank = 'Saint-Ranked Mushoku Fan'
  elif user_points >= 800:
    rank = 'Advanced Mushoku Fan'
  elif user_points >= 400:
    rank = 'Intermediate Mushoku Fan'
  elif user_points >= 150:
    rank = 'Beginner Mushoku Fan'
  else:
    rank = 'None'

  return rank
#Fuction to check if given response is the right answer
def check_answer(correct_answer, response):
  if response == correct_answer:
    return True

  elif isinstance(correct_answer, list) and (response in correct_answer):
    return True
          
  else:
    return False   

async def create_embed_response(correct_answer, response, channel):
  if correct_answer == True:
    title_msg = "Great Answer ! :white_check_mark: (+10 MT Points)"
  else:
    title_msg = "That doesn't seem right :x:"
  embedded = discord.Embed(title = f"{title_msg}", description = f"{response}")
  await channel.send(embed = embedded)
  return
        
client.run(token)

# The following line is optional: it removes the reaction added by the user 
        #await reply.remove_reaction(reaction, user) 
                  
#@client.event
#async def on_reaction_add(reaction, user):
  #await reaction.message.channel.send(f"{user} reacted with {reaction.emoji}")
