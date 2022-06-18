import discord
import ffmpeg
import nacl
import requests
import json
import asyncio
import random
import os
from dotenv import load_dotenv

from questions_bank import questions
from choices_bank import choices
from responses_bank import responses


#token and verification
#keep_alive()
load_dotenv()
token = os.getenv('MUSHOKU_BOT_TOKEN')
client = discord.Client()

round_ongoing = False
guess_round_ongoing = False

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
    
    if msg.lower() == "mt points":

      #print user's current points
      #Idea- rankup only during points check maybe (play fanfare)
      if user_id in users:
        with open("users.json","r") as file:
          user_points = users[user_id]["Points"]
          rank = rank_check(user_points)
          rank_change = rank_write(message, rank)
          if(rank_change):
            await message.channel.send("Congratulations {} ! You've ranked up to '{}' ! Keep up the good work !".format(user.mention, rank))
          await message.channel.send("{}'s Adventurer Log\n------------------------------------\nMT Points ({})\nRank - {}".format(user.mention, user_points, rank))

      #track new user
      else:
        with open("users.json","w") as file:
          users[user_id] = {}
          users[user_id]["Points"] = 0
          users[user_id]["Rank"] = "None"
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('New adventurer detected ! \nWelcome {}! Your points are now being tracked'.format(user.mention))

    #clear all points
    if msg == "MT Points Clear":
      with open("users.json","w") as file:
          users[user_id]["Points"] = 0
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('All points cleared')

    #clear all points
    if msg == "MT Points 2500":
      with open("users.json","w") as file:
          users[user_id]["Points"] = 2500
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('MT Points set to 2500')

		

  #guess game mode
  async def guess_mode():

    #question bank
    questions = ["What is the name of Rudeus's Master ?"]
    
    #choices correspond to questions.keys()
    answers = [['Roxy','Roxy Migurdia']]
    
    random_number = random.randint(0, len(questions)-1)
    question = questions[random_number]
    answer = answers[random_number]
    
    #send question as an embed
    embedded = discord.Embed(title = f"{question}")
    bot_message = await message.channel.send(embed = embedded)
    
    
    #Check user answer
    async def answer_check(answer):
      try:          
            #Add clock here
            while True:
              guess = await client.wait_for('message', timeout=8)
              guess = str(guess.content)
        
              if guess in answer:
                await message.channel.send('Correct')
                turn_off_round2() 
                break

              if guess.lower() == ('mt stop'):
                await message.channel.send('Round stopped.')
                turn_off_round2() 
                break
          
              else:
                continue 
    
      #stop round if time limit exceeded
      except asyncio.TimeoutError:
        await message.channel.send('Timeout, try to answer quicker next time')
        turn_off_round2()  
      

    await answer_check(answer)
        
  #trivia game mode
  async def trivia_mode():
    bot_message = ''
    reactions = ["🇦", "🇧", "🇨", "🇩", "🇪"]
    
    random_number = random.randint(0, len(questions)-1)

    question_keys = list(questions.keys())
    question = question_keys[random_number]
    choice = choices[random_number]
    response = responses[random_number]
    choices_message = '\n'.join(choice)
    correct_answer = questions.get(question)

    #send question as an embed
    if len(question+choices_message) >= 256:
      embedded = discord.Embed(title = f"{question}",description = f"{choices_message}")
      
    else:
      embedded = discord.Embed(title = f"{question}\n{choices_message}")
      
    bot_message = await message.channel.send(embed = embedded)
    for i in range (len(choice)):
        await bot_message.add_reaction(reactions[i])

      
    #Check and return reaction user and all available reactions
    def check(reaction, user):
        reacts = ["🇦", "🇧", "🇨", "🇩", "🇪"]
        if user == client.user:
          return
        else:
          return user == message.author and str(reaction.emoji) in reacts
        

    try:
      reaction, user = await client.wait_for('reaction_add', timeout=55.0, check=check)
    
    #Stop round if time limit exceeded
    except asyncio.TimeoutError:
      await message.channel.send('Timeout, try to react faster next time')   
      turn_off_round()     

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
                  users[user_id] = {}
                  users[user_id]["Points"] = 10
                  users[user_id]["Rank"] = "None"
                  json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
                  await message.channel.send('New adventurer detected ! \nWelcome {}! Your points are now being tracked'.format(user.mention))
                             
            await add_points(user)

          global round_ongoing
          round_ongoing = False
          return
        

  #Easter egg
  if message.content.startswith("klu"):
    chance = 1
    random_number = random.randint(0, 10)
    if random_number == chance:
      await message.channel.send('klu deez nuts bro', delete_after=0.1)
      
    if random_number == (chance+1):
      await message.channel.send('klu deez nutzzz 🥜🥜', delete_after=0.1)

  #Function to join voice channel and play music
  async def play_ost():
      try:
        connect_voice = user.voice
        vc = await connect_voice.channel.connect()
        vc.play(discord.FFmpegPCMAudio(source='Tabibito no Uta.mp3',executable='./ffmpeg.exe'))

        #Listen for stop command
        async def stop_ost():
          try:          
                while True:
                  stop_command = await client.wait_for('message', timeout=300)
                  stop_command = str(stop_command.content)

                  if stop_command.lower() == ('mt ost stop'):
                    await vc.disconnect()
                    await message.channel.send('Stopped the music.')
                    break
              
                  else:
                    continue 
        
          #Leave voice channel when time limit exceeded
          except asyncio.TimeoutError:
            await message.channel.send('Leaving voice channel...')
      

        await stop_ost()

      #Exception for no voice channel id
      except(AttributeError):
        await message.channel.send('Hmm ? Are you in a voice channel now ?')          

  #Voice channel command
  if msg.lower() == ("mt ost"):
    await play_ost()

  #Trivia quiz command
  if msg.lower() == ("mt trivia"):
    global round_ongoing
    if round_ongoing == False:
      round_ongoing = True      
      await trivia_mode()
    else:
      await message.channel.send('There is a trivia round ongoing ! Finish it first !')

  #Guess round command
  if message.content.lower().startswith("mt guess"):
    global guess_round_ongoing
    if guess_round_ongoing == False:
      guess_round_ongoing = True      
      await guess_mode()
    else:
      await message.channel.send('There is a guess round ongoing ! Finish it first !')
      
  #Help message command
  if message.content.lower().startswith("mt help"):
    channel = message.channel
    await display_embed(channel)

#Function to display help menu
async def display_embed(channel):
    embed = discord.Embed(
        title = 'Available Commands', description = 'Changelog\n--------------\nVer 0.12 - 40 total trivia questions, new guess game mode (beta)\nVer 0.11 - Adds 6 trivia questions and an easter egg\nVer 0.1 - Trivia mode and point system',
        colour = discord.Colour.orange()
    )

    embed.set_footer(text='In development v0.12')
    embed.set_image(url='https://media.discordapp.net/attachments/905934829659496458/920654143721467944/Mushoku_Tensei_Isekai_Ittara_Honki_Dasu_Logo_Japones.png')
    file = discord.File("thumbnail2.png")
    embed.set_thumbnail(url="attachment://thumbnail2.png")
    embed.set_author(name = 'MushokuBot Help', icon_url='https://cdn.discordapp.com/attachments/905934829659496458/920656680830791740/286158_-_Copy.jpg')
    embed.add_field(name=':scroll: MT Trivia', value = 'Start a round of Mushoku Tensei trivia !', inline = True)
    embed.add_field(name=':diamond_shape_with_a_dot_inside: MT Points', value = 'View your current MT points', inline = True)
    embed.add_field(name=':thought_balloon: MT Guess', value = 'Type the correct answer to win', inline = True)
    embed.add_field(name=':musical_note: MT OST', value = 'Play Mushoku Tensei Soundtracks', inline = True)
    embed.add_field(name=':grey_question: MT Help', value = 'View all available commands', inline = True)

    await channel.send(file = file, embed=embed)

#Function to determine user rank based on points
#Idea - add custom messages for each rank up
def rank_check(user_points):
  if user_points >= 10000:
    rank = '***God-level Mushoku Ultra Fan***'
  elif user_points >= 4500:
    rank = '***Emperor***-Tier Mushoku Fan'
  elif user_points >= 2000:
    rank = '**King-Tier** Mushoku Fan'
  elif user_points >= 1400:
    rank = '**Saint**-Ranked Mushoku Fan'
  elif user_points >= 800:
    rank = 'Advanced Mushoku Fan'
  elif user_points >= 400:
    rank = 'Intermediate Mushoku Fan'
  elif user_points >= 150:
    rank = 'Beginner Mushoku Fan'
  else:
    rank = 'None'

  return rank
  
def turn_off_round():
      global round_ongoing
      round_ongoing = False 

def turn_off_round2():
      global guess_round_ongoing
      guess_round_ongoing = False 

#Writes user rank to file
def rank_write(message, rank):
  with open("users.json","r") as file:
    users = json.load(file)
    user = message.author
    user_id = str(user.id)
    old_rank = users[user_id]["Rank"]
    
  with open("users.json","w") as file:
    users[user_id]["Rank"] = rank
    json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)

  if rank != old_rank:
    return True

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
