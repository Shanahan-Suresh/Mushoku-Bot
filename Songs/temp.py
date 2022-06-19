#trivia game mode
async def trivia_mode():
    bot_message = ''
    reactions = [":one:", "🇧", "🇨", "🇩", "🇪"]
    

    #send question as an embed
    embedded = discord.Embed(title = f"Song List",description = f"Test")
      
      
    bot_message = await message.channel.send(embed = embedded)
    for i in range (len(reactions)):
        await bot_message.add_reaction(reactions[i])

      
    #Check and return reaction user and all available reactions
    def check(reaction, user):
        reacts = [":one:", "🇧", "🇨", "🇩", "🇪"]
        if user == client.user:
          return
        else:
          return user == message.author and str(reaction.emoji) in reacts
        

    try:
      reaction, user = await client.wait_for('reaction_add', timeout=55.0, check=check)
    
    #Stop round if time limit exceeded
    except asyncio.TimeoutError:
      await message.channel.send("Timeout, let me know when you've decided on a song")       

    #carry on if reaction given
    else:   
          channel = message.channel
      
          if reaction.emoji == ":one:":
              await message.channel.send("One")
            
          elif reaction.emoji == "🇧":
              await message.channel.send("B")
            
          elif reaction.emoji == "🇨":
              await message.channel.send("B")
         
          else:
              await message.channel.send("Sorry, I can't play a song I don't know")

          return