import discord
import os
import requests
import json
import asyncio
import random
from keep_alive import keep_alive

#token and verification
#keep_alive()
token = os.environ['TOKEN']
client = discord.Client()

round_ongoing = False

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
    if msg == "MT Points 800":
      with open("users.json","w") as file:
          users[user_id]["Points"] = 800
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('MT Points set to 500')

		

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
    "What's Eris's middle name ? (Eris ___ Greyrat)": ['B','E'],
    "Dragon God Orsted is currently the strongest living being in the world." : 'A',
    "Currently, the strongest human in the world is..." : 'B',
    "Rudeus has two little sisters, named:" : 'B',
    "The Green ore coin is the highest valued coin on the Demon Continent.\nHow many Asuran Gold Coins is one of them worth ?" : 'D',
    "Armored Dragon King, Perugius Dola is famous for...." : 'C',
    "The most dangerous continent in the world is said to be the..." : "D",
    "Why is the Teleportation Labyrinth regarded as the most dangerous dungeon in the world ?" : "A",
    "The 'Strife Zone' is..." : "C",
    "Before Zenith became an adventurer in Paul's party, she was...?" : "D",
    "The spears wielded by Supard warriors come from...?" : "C",
    "God-tier healing magic is capable of reviving even the dead." : "B",
    "Paul's adventuring party was known as '____', and they were a(n) _ tier adventuring party" : "A",
      "Ghislaine Dedoldia is also called ___ by some people." : "C",
      "Who started the First Great Human-Demon War ? " : "D",
      "Who started the Second Great Human-Demon War ? " : "A",
      "Who started the Third Great Human-Demon War ? " : "C",
      "During Laplace's War, Perugius and his six comrades became known as 'The Seven Heroes'. Which of these were not one of them ?\n(hint: think logically)" : "B",
      "Which one of the following did not take part during the final battle against Laplace during the Third Great Human-Demon War ?\n(choose the most likely answer)" : "D",
      "___ was held responsible for the Mana Calamity(Teleportation Incident) and sentenced to execution." : "D"
    }

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
              ["A. Notos","B. Boreas","C. Euros", "D. Zephyrus", "E. (No Middle Name)"],
              ["A. True","B. False"],
              ["A. Dragon God Orsted","B. Sword God, Gal Farion", "C. Nanahoshi Shizuka (Silent Seven Stars)", "D. Saint Milis", "E. Ars, the Hero of Humanity"],
              ["A. Aish and Julie","B. Aisha and Norn","C. Lilia and Zenith", "D. Lucy and Lara"],
              ["A. 100","B. 10","C. 1","D. 0.01"],
              ["A. Aiding the First Dragon God's destruction of all 6 other worlds.","B. Achieving true bankai at the age of 3","C. Defeating Demon God Laplace during the Third Great Human-Demon War","D. Opening a restaurant that made deep fried chicken"],
      ["A. Central Continent","B. Begaritt Continent","C. Heaven Continent","D. Demon Continent"],
      ["A. Because of the teleportation traps of course !","B. Because of the 9-headed hydra deep within its depths","C. Because of the bloodthirsty monsters inside it","D. Because of the nearby empire of human-sized ants, numbering in the thousands"],
      ["A. A term to describe a particular formation of monsters, often used by adventurers.","B. The term used to describe Advanced-rank swordsmen who aspire to rise to the Saint-rank.","C. A region full of conflicting nations within the Central Continent.","D. A region full of conflicting Demon Lords in the Demon Continent."],
      ["A. a famous healer","B. a school teacher","C. a poor farm girl","D. a noble lady"],
      ["A. the strongest metal in the Demon Continent, Bofadeez","B. the hide of their first hunted dragon","C. their tails","D. their own ancestors, passed down through history"],
      ["A. True","B. False"],
      ["A. Fang of the Black Wolves...S","B. Paul's Merry Adventurers...A","C. Fittoa Search and Rescue...A","D. Steppe Ladder...S"],
      ["A. Mad Dog","B. Mad Sword King","C. The Forest Goddess","D. Black Fang Sword King"],
      ["A. Ars, the Hero of Humanity","B. Fighting God ||Alderaan(?)|| ","C. Demon God Laplace","D. Kishirika Kishirisu, the Great Demon Empress"],
      ["A. Kishirika Kishirisu, the Great Demon Empress","B. Dragon God ||Laplace|| ","C. Fighting God ||Alderaan(?)||","D. Technique God Laplace"],
      ["A. Armoured Dragon King, Perugius","B. Kishirika Kishirisu, the Great Demon Empress ","C. Demon God Laplace"],
      ["A. North God Kalmon I","B. North God Kalmon III","C. Fire Emperor Feroze Star", "D. Dragon God Urupen", "E. Gaunis Freean Asura, the Queen of Asura"],
      ["A. Armoured Dragon King, Perugius","B. North God Kalmon I","C. Ruijerd Superdia", "D. Fire Emperor Feroze Star"],
      ["A. Kenya Boreas Greyrat","B. Hilda Boreas Greyrat","C. Philip Boreas Greyrat","D. Sauros Boreas Greyrat"]
      
              ]

    #responses correspond to choices
    responses = [
              ["Come on bro, did he look that young ?","Close, but not quite","That's right, you got it !","If he was that old, he might've died from a heart attack instead."],
              ["Terrifying, but not right.","Although most people believe he's evil, nobody calls him this.","Correct ! He's known as 'Dead End' because those who meet him have their fates cut short (i.e reach a dead end in thier lives) , or so the rumour goes.","A more accurate name out of all the choices.\nSadly, very few people regard him as such.", "Also correct ! He's known as Guard Dog Ruijerd of Dead End during his time partying up with Rudeus and Eris. "],
              ["A demon huh ? Although its true that Ghylaine's race often intermingles closely with the Demon race, she isn't a half-breed. Better luck next round !","Right ! Did her tail and fluffy ears give it away ?","Sorry to say, there is no such race in Mushoku Tensei's world","What even is a 'Forestor' ? Someone who lives in a forest ? I sure don't know."],
              ["A Migurd's body stops aging during their teen years, so I can see why you would think that.","Roxy first left her home and became an adventurer around this periord of her life. It will be some time before she eventually meets Rudeus.","Fun fact: Roxy and Rudeus are both mentally the same age !","Well... she would look the same even if she was this old. Good guess ?"],
              ["Lilia was the daughter of the sword master in the dojo where Pual first picked up swordsmanship. They parted ways after Paul bedded her and ran away from the dojo.","While Paul was living the life of an adventurer, Lilia was serving within the Asura Capital's palace as a royal handmaiden. They did not meet each other during this period of their lives.","Paul and Zenith retired from adventuring after getting married. At this point, they could handle themselves quite well and did not need to hire a maid.","Lilia left her service within the Asuran Palace due to an injury during an assasination attempt on the newborn princess. She was then hired by Paul shortly before Rudeus was born to take care of Zenith's home duties while she was expecting.\n\nHowever, this was not their first meeting."],
            ["Although Sylphy does have human blood running within her, it wouldn't be accurate to call her one as most of her characteristics originate from another heritage.","Her green hair may give off the impression that she's a demon. But she has no demon heritage. The cause of the green hair is instead because of....||the 'Laplace Factor'||","Technically correct ! Her father is half elf, half human, while her mom is a mix of human and beastfolk.","Absolutely right ! Her father is half elf, half human, while her mom is a mix of human and beastfolk. You sure know your stuff !", "A mixed person borne from these 2 races is very common, but Sylphy isn't one of them."],
          ["Ruijerd is pretty old, but the first Human-Demon War took place ~10,000 years ago. An average Supard lives for 500~1000 years, so Ruijerd likely wasn't even born during that period.","Ruijerd has only been confirmed to serve during the 3rd Human-Demon War (aka Laplace's War). He was one of the most important figures during the war, his efforts shaping the current landscape of the world."],
        ["When he first started learning magic at the age of 2, Rudeus quickly blew past the intermediate stage for almost all schools of magic because of his innate understanding of physics and science.","The magic spells Rudeus used at the age of 3~4 were of this tier. Most of his other schools of magic remain at this tier way long pass his days adventuring in the Demon Continent.", "That's right. Rudeus reached Saint tier at the age of 5. For reference, the most esteemed professors of the best magic university in the world stuggle for most of their lives to reach this rank. It's also why almost no way except those that are close to Rudeus believes this accomplishment.", "Reaching King-ranked magic would engrave you solidly within the history books. It may take some more time before Rudeus can reach this level, but he definitely has the potential ! ", "Emperor-tier magic is found far and few within even the entire history of the world. Currently the number of people capable of even using such powerful magic are countable on a single hand."],
        ["All three of these sword styles were founded by their respective gods centuries ago. Currently, the Sword God Style is the most popular of the three.","Were you thinking of another series ?", "Neither the Dragon God nor the Demon God uses a weapon (they don't need one), and they definitely don't have a sword style under their name."],
      ["The first prince was 32-years old when Rudeus entered Shirone, definitely couldn't be a brat like Pax !","The third prince is the chad Zanoba. Wayyy better than Pax.","The 4th prince had his head ripped apart by Zanoba shortly after he was born \n(by accident of course !). Too bad it wasn't Pax instead....","Right. Pax is nearly last in line for ascending the throne of the Shirone kingdom.... hopefully he never does !"],
      ["As one of the two sole surviving human nations emerging victorious from Laplace's War, Asura kingdom is rich in both economic and military might, making it the world's strongest superpower nation. Unfortunately, with no threats from the outside, the Asuran royalty and Asuran nobles have been infighting for the last few decades, leaving a good chance for other nations to overtake Asura.","As one of the two sole surviving human nations emerging victorious from Laplace's War , the Holy Milis Kingdom is strong in terms of holy magic and military might. Unfortunately, their isolation with the surrounding demonic kingdoms and distance from other human nations makes their economy fall short.","The Kingdom of the Dragon King is a fast growing nation, recently subjugating many nearby smaller nations. Though they still don't have nearly enough military might to take on great nations like Asura or Holy Milis, frailer nations such as Shirone fall within the threat of their blades.","In terms of magic prowess, the Three Magic Nation Alliance are definitely the pinacle of the world. Though, their efforts are mainly directed towards the progression of magical advancements within society, which leaves them little concern with political or military issues."],
      ["Monsters aren't a race, do you consider animals a race ? And 'Gods' are ranks or titles, they aren't a seperate group of races.","Both elves and dwarfs fall under the category of Beastfolk. This is because the proximity of beastfolk and demon races across hundreds of centuries have led to a variety of new sub-races, which include elves(mainly beastfolk), dwarfs(mainly beastfolk), ogres(mainly demon race), etc.","You got it right ! Both mermaids and angels exist in Mushoku Tensei's world, though it's not likely you'll see any characters from these two races anytime soon (they're VERY seclutive !)."],
      ["Maybe in another timeline......","Right ! Eris is from a branch of the Boreas family, she has 2 older brothers in the royal capital belonging to the main branch. They were sent there to avoid potential uprisings to the main family from a branch family like Eris's.\nGosh, it's pretty complicated.","Euros is one of the 4 noble Greyrat branches, but not Eris's branch.", "Zephyrus is one of the 4 noble Greyrat branches, but not Eris's branch.", "Well... that's true at some point.\nBut I'm sure you knew that, so it's not a spoiler. Right ?"],
      ["Although Orsted only holds the 2nd rank on the 'Seven Great Powers'.\nThe highest ranked being, the 'Technique God' doesn't exist at the moment.\nThus, Orsted is definitively the strongest creature in the world.","Do you know of someone stronger than than the Dragon God ?"],
      ["Orsted is certainly very strong. In fact, he's currently the strongest living being in the world at the moment. But he's not human dude. Was the 'Dragon' part not clear enough ?","Right, at this point in time, Sword God Gal Farion is the only pure human that made it into the ranks of the 'Seven Great Powers'. His blade can swing faster than the speed of light, his stregth rivals even the military might of entire nations, he's a terrifying man. Would be a shame to get on his bad side....", "Silent Seven Stars is gifted in the brains section and has made many noteworthy contributions to magical and culinary advancement. However, she is not particularly strong when it comes to combat strength (quite the opposite in fact).", "The strength of Saint Milis is undefined. It's said that the entirety of Saint Milis road was created with a single swing of his holy blade. Regardless of his true strength, Saint Milis lived is said to have lived many centuries ago during the inception of the Holy Kingdom of Milis. As a human, it would be unbeliveble for him to survive up till this point in time.", "Ars, if he really existed, is likely the strongest human in the history of the world. Along with his six comrades, he had defeated Kishirika Kishirisu, the Great Demon Empress and her Five Great Demon Kings during the First Great Human Demon War, protecting humanity's prosperity and peace for eons to come.\nThat was a long time ago though, he's not alive today."],
      ["Aishcream and Julie's biscuits please.","Aren't they the cutest ?","You must be joking....", "Those aren't his sisters, silly."],
      ["You'd be right if the question was the other way around.","Nope, try again.","The Demon Continent is the poorest and most inhospitable place to live. Their money isn't worth a 1 to 1 exchange with Asura, the richest nation in the world.","That's right ! It takes about a hundred Green Ore coins to reach the value of 1 Asuran Gold Coin. Fun fact, the official checkpoint charges around 200 Green ore coins for a Supard to cross into Milis Continent's Zanto port. They really don't like the Demon race, especially Supards !"],
      ["Although Perugius was alive during this point in time, he was just a child and did not play a role in the Dragon God's terror.","You forgot the part where he mastered Sage Mode and found the One Piece too.","That's right, out of the 7 heroes that defeated Demon God Laplace, Perugius is the most famous of them all.\n\nHe displayed the magnificence of his powers throughout the war against Laplace. Perugius made use of his greatest strength, summoning magic, to call forth twelve familiars: Void, Dark, Bright, Surge, Life, Violent Earthquake, Time, Roaring Thunder, Destruction, Insight, Insanity, and Atonement. These were the aliases of his strongest familiars.\n With them, Perugius restored the old floating fortress [Chaos Breaker] and headed into the final battle against Laplace.\nYet all that power was not enough to completely destroy the Demon God, forcing Perugius to settle for sealing him away instead.\n\nWith the end of that war, humanity proclaimed the start of a new era. Which is the current era, the Armored Dragon Era, named after him for his great service to the world.","I believe you're thinking of Death God Randolph. By the way, his fried chicken absolutely sucked ! Rudeus said so himself."],
      ["With it's rich peaceful farmlands and relatively weak monsters, the Central continent is in fact the safest continent to live in.","The Begaritt Continent houses extremely violent monsters, and is where the most infamous dungeons in the world can be found. However, it is not the most dangerous continent.","Although the path to reach the Heavon continent is full of strive and dangers, the continent itself is mostly peaceful. Though not much is known about it.","Correct. In the Demon Continent, D-rank monsters and above are a common sight to see roaming around the outskirts of towns and cities. Many warriors travel to the Demon continent to train, but most never come back. It is an exceedingly harsh land ruled by a number of minor warring Demon Lords.\n\nThe worst thing that could happen is suddenly finding yourself stuck there. But what are the chances of that happening ?"],
      ["Exactly. True to its name, the Teleportation Labyrinth is full of near-undetectable teleportation traps that could completely destroy a party's formation. In worst cases, the teleported person could find themselves face-first with a horde of hungry monsters. Yikes !","Although a hydra may or may not actually be within its depths, that is not the reason why people consider this dungeon dangerous.","All dungeons have bloodthirsty monsters which evolved from the dense concentration of mana, it doesn't make it particularly dangerous though.","Although on the same continent, the empire of human-sized ants is not close to the Teleportation Labyrinth. They aren't as dangerous either since they're being sealed within four magic barriers created by a certain Dragon God."],
      ["It sounded that believable huh ?","Strive to get the answer right the next time !","That's right ! The Strife Zone constantly sees the rise and fall of dozens of small nations within even a single decade. Although the conflicts may not be large-scale, the sheer number of them have led people to call it as such.","I believe places with fighting Demon Lords are simply called a war zones :)"],
      ["Zenith became very adept at healing magic before her adventuring days, but she wasn't famous nor did she make a living from it. ","Zenith seems to be good with kids, she probably would have made a good school teacher.","She may give off that immpression sometimes, but that just isn't the truth.","That's right ! Zenith was the second daughter of a noble count family within the Holy Milis Kingdom. She learned healing magic because it was part of her education as a noble lady. She ran away from home at the age of fifteen after a fight with her parents, and became an adventurer soon after. Pretty similar to Paul, I would say."],
      ["Bofa DEEZ NUTZ ! HAH ! Got eem!","There aren't any known dragons in the Demon Continent. It's filled with other scary monsters though.","All Supard are born with a three-pointed tail. It grows with them until they reached a certain age, at which point it would stiffen up and fall off. Yet even when separated, it's somehow part of their body. The more they use it, the sharper and more deadly it would grow. With enough time and effort, these tridents could become peerless weapons, virtually unbreakable and capable of piercing through pretty much anything. Supards usually never cast aside their spears, not until the day they die.","A spear passed down through history would probably break easily though ? No ?"],
      ["Maybe in other series. But nothing can restore a life that's over in Mushoku Tensei. Even immortal beings would not be able to revive if they truly lost their lives.","That's right. Not even God-tier healing magic can bring back a lost life. But it CAN save those whose bodies are being destroyed. An example would be God-Tier magic may be used to completely stop the Magic Stone Disease, which is an uncurable disease that slowly turns the infected person's body to rock hard granite."],
      ["That's right. They were a solid adventuring party consisting of Zenith the healer, Ghylaine the frontline, Paul the midguard, Elinalize the tank, Talhand the magician, and Geese the 'all-around handyman'","Paul's ego is big, but not THAT big... probably.","Paul created the 'Fittoa Search and Rescue' team after the Teleportation incident, its not the name of his party during his adventuring days.","Steppe Ladder is a famous S ranked party during Rudeus's adventuring days, not Paul's."],
      ["She's close to the person called 'Mad Dog', but it's not her.","'Mad Sword King' is held by another familiar character in the series, but not Ghyslaine.","Correct ! Ghyslaine got this nickname after she helped a struggling nation within the Strife Zone during the Teleportation incident. With her efforts during a hopeless battle against 2 larger nations, she helped them earn a decisive victory.\n\nAt the time, she did not give her name, so the soldiers called her 'The Forest Goddess'. Her mystic figure was passed down through the nation's history and culture. \n\nEven hundreds of years later, 'The Forest Goddess' remains a prominent symbol of hope for that nation's people. Though, Ghyslaine herself will never know this.","She's actually also known as 'Black Wolf Sword King', but not 'Black Fang Sword King'."],
      ["Ars was the person who ENDED the war, not started it.","Although the Fighting God was around during this period of time, he didn't take part in the First Great Human Demon War, only the Second.","The First Great Human Demon War took place before the creation of Demon God Laplace. Try guessing another ancient being next time.","Correct ! Along with her Five Great Demon Kings, Kishirika Kishirisu rose as the Great Demon Empress, leading all demon races in a united battle against humanity, lasting a thousand years."],
      ["A thousand years following her death, a revived Kishirika Kishirisu launches the Second Great Human-Demon War. This time, persuading both the Beast and Sea races to join the war on the Demon's side. Humanity was pushed to the brink of extinction after several centuries of fighting. Unfortunately for her, humanity persuaded Dragon God ||Laplace|| to join their side, leading to the Demon forces' crushing defeat.","Although Dragon God ||Laplace|| was part of the war, he only joined after being persuaded by humanity on during the brink of thier defeat. ","Althought Fighting God ||Alderaan(?)|| was part of the war, he only joined as a response||(you know if you know)|| to Dragon God ||Laplace||'s intervention.' ","The Technique God Laplace's existence resulted from the conclusion of the Second Great Human-Demon War. He was a byproduct, not a causation."],
      ["Armoured Dragon King Perugius didn't start the war. But he is often credited as the most important person during the conflict. Along with his 6 companions and 12 familiars, he won the battle for humanity's greatest struggle, ending the bloodiest conflict in recent history.","Hah ! A third time ? Unlikely.","Following his revival, Demon God Laplace starts a new Great Human-Demon War. After successfully uniting all the demon races and convincing both the Sea and Beast races to join his side, he started the most brutal conflict the world has seen. After a century of fighting, most of humanity was destroyed, only the Asura and Holy Milis Kingdom remained. Nearing the end, heroes from all corners of the world, and the remaining humans gathered in the town of Roa in order to have a final stand against the demons. Against all odds, they triumphed."],
      ["Incorrect Kalmon I did indeed join the war on the side of his good friend Perugius. But now it's obvious what the is answer for this question, right ?","Right, this was logically guessable since there can only be one North God at a time. Fun fact, Kalmon I and Kalmon III are both from the same lineage. The former being the grandfather of the latter.","Fire Emperor Feroze Star was one out of the 4 heroes of The Seven who fell in battle during the war. His sacrifice leading the way for victory in the end.", "Dragon God Urupen, the 99th Generation Dragon God, is often known as the weakest Dragon God in history. But his strength proved vital in Laplace's ultimate defeat.", "Gaunis Freean Asura took the throne following her father's and brothers deaths. She lived past the end of the war, and led Asura's grand restoration during peacetimes."],
      ["Perugius was among those who defeated Laplace during the final battle. Unable to destroy his soul, Perugius opted to seal him away instead, ending the war.","It is said that only 3 among the Seven Heroes survived the war. North God Kalmon I, being one of them, is likely to have participated in the final fight against Laplace","During the final fight, at a critical moment, Ruijerd Superdia appeared and stabbed Laplace as revenge for Laplace's ploy against the Supards. Opening up the opportunity for Perugius and the remaining heroes to defeat Laplace once and for all.", "Fire Emperor Feroze Star is the only one among The Seven to have been confimed to perish during Laplace's War. Before his death, he named his unborn child in case he wouldn't make it back in time for his birth. As such, it became taboo to name your child before heading of on a journey in this world.\n\nIt isn't stated whether he died during or before the final fight, but he is the least likely to have participated out of the choices."],
      ["Kenya fit Deez Nutz in your mouth ? HAH ! Got eem !","Neither Hilda nor Philip were executed. Likely due to them already being confirmed dead. Remnants of their bodies were discovered within the Strife Zone shortly after the Teleportation incident. RIP Hilda.","Neither Hilda nor Philip were executed. Likely due to them already being confirmed dead. Remnants of their bodies were discovered within the Strife Zone shortly after the Teleportation incident. RIP Philip.","The execution of Sauros Boreas Greyrat served multiple purposeses. First, it appeased the masses and redirected thier ire away from the Royal Family, instead pointing the blame on Sauros. Second, it protected the main Boreas family line from being extinguished. Sauros served as an ideal scapegoat for his son, the current head of the Boreas family, who was on the brink of losing power due to harsh political intrigue resulting from the Teleportation Incident."]
              
              ]
    
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


    #answered = False
      
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
        


  if message.content.startswith("MT Trivia"):
    global round_ongoing
    if round_ongoing == False:
      round_ongoing = True      
      await trivia_mode()
    else:
      await message.channel.send('There is a trivia round ongoing ! Finish it first !')
      

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
	embed.add_field(name=':scroll: MT Trivia', value = 'Start a round of Mushoku Tensei trivia !', inline = True)
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
  
def turn_off_round():
      global round_ongoing
      round_ongoing = False 
  
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
