#!/usr/bin/python3

import discord
from discord.ext import commands
import asyncio
import os
from lib.PDO import PDO
from AlwaysUpdate import AlwaysUpdate
import os
from dotenv import load_dotenv
from datetime import datetime
from lib.API import API

load_dotenv()

bot = commands.Bot(command_prefix="/", description="Le guide du routard", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Bot ready !")

bot.remove_command("help")
@bot.command()
async def help(context):
    message = ">>> ## **Au secours**\n"
    message += "\n"
    message += "Le guide du rootard saura te mener sur le bonne root\n"
    message += "\n"
    message += "- **/help** : Affiche ce message"
    message += "- **/ping** : pong"
    message += "- **/pong** : ping"
    message += "- **/status** : Donne le statut des différentes variables"
    message += "- **/getUsers** : Liste les utilisateurs enregistrés"
    message += "- **/addUser username** : Ajoute un utilisateur à la base de données"
    message += "- **/enableGlobalNotifications** : Défini un salon comme cible pour les notifications de flag"
    message += "- **/createGlobalScoreboard** : Crée un scoreboard global qui se mettra à jour automatiquement"
    message += "- **/update** : Met à jour chaque utilisateur avec les informations de root-me"
    message += "- **/scoreboard** : Affiche le scoreboard"
    message += "\n"
    await context.send(message)


@bot.command()
async def ping(context):
    await context.send(">>> pong")

@bot.command()
async def pong(context):
    await context.send(">>> ping")

@bot.command()
async def status(context):

    global alwaysNotifyFlagz
    global globalScoreboardLaunched
    global globalScoreboardShouldBeUpdated
    global lastUpdate

    message = ">>> **Status**\n\n"
    message += f"**Notifier lors d'un flag :** {alwaysNotifyFlagz}\n"
    message += f"**Le scoreboard est mis à jour automatiquement :** {globalScoreboardLaunched}\n"
    message += f"**Le scoreboard doit va être mis à jour prochainement :** {globalScoreboardShouldBeUpdated}\n"
    message += f"**Dernière update :** {lastUpdate}\n"

    await context.send(message)

@bot.command()
async def getUsers(context):
    users = pdo.getUsers()
    message = ">>> **Les utilisateurs :**\n\n"
    try : 
        for user in users : 
            message += f"- {user[0]}\n"
    except :
        pass

    await context.send(message)




@bot.command()
async def addUser(context,username):
    """Ajoute un utiliateur à la base de données. La casse doit correspondre

    Usage : /addUser Username

    Args:
        context (ctx): the discord channel from where the bot is called
        username (string): the username
    """
    if len(username) > 0 :
        
        res = api.getUser(username)
        timer = 5
        while "status_code" in res.keys() and res["status_code"] == 429 :
            await asyncio.sleep(timer)
            res = api.getUser(username)
            timer += 5

        if "status_code" in res.keys() and res["status_code"] == 404 :
            await context.send(">>> **Utilisateur introuvable** \n\nVérifiez que le nom renseigné est bien celui avec lequel vous accédez au profil public avec https://www.root-me.org/USERNAME")
            return 

        resp = pdo.insertUser(username)
        if not resp : 
            await context.send(">>> **Utilisateur existant**")
        else :
            await context.send(f">>> **Utilisateur {username} ajouté**")


@bot.command()
async def enableGlobalNotifications(context):
    """Automatically search for any flag or new information in root-me public profiles of users

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    global alwaysNotifyFlagz
    global ranking
    global globalScoreboardShouldBeUpdated
    global lastUpdate

    if alwaysNotifyFlagz :
        await context.send("Les mises à jours automatiques sont déjà activées")
        return

    alwaysNotifyFlagz = True
    await context.send("Activation des mises à jour automatiques")
    while True :
        print("running")
        os.system('echo "Last run : $(date)" >> /tmp/logs.txt')
        for user in pdo.getUsers() : 
            username = user[0]

            print(f'Looking for {username}')

            maj = await AlwaysUpdate.getUpdate(username)
            
            if username not in ranking.keys() :
                globalScoreboardShouldBeUpdated = True
                ranking[username] = maj["points"]

            for img in maj["images"] :
                ranking[username] = maj["points"]
                globalScoreboardShouldBeUpdated = True
                with open(img ,'rb') as f:
                    picture = discord.File(f)
                    await context.send(file=picture)
                os.remove(img)
            await asyncio.sleep(10)

        lastUpdate = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        await asyncio.sleep(7200) # 2h


@bot.command()
async def update(context):
    """Search for any flag or new information in root-me public profiles of users

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    global alwaysNotifyFlagz
    global ranking
    global globalScoreboardShouldBeUpdated
    global lastUpdate

    await context.send(">>> **Recherche de mises à jour**")

    print("running")
    os.system('echo "Last run : $(date)" >> /tmp/logs.txt')
    for user in pdo.getUsers() : 
        username = user[0]

        print(f'Looking for {username}')

        maj = await AlwaysUpdate.getUpdate(username)
        
        if username not in ranking.keys() :
            globalScoreboardShouldBeUpdated = True
            ranking[username] = maj["points"]

        for img in maj["images"] :
            ranking[username] = maj["points"]
            globalScoreboardShouldBeUpdated = True
            with open(img ,'rb') as f:
                picture = discord.File(f)
                await context.send(file=picture)
            os.remove(img)

    lastUpdate = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    if not globalScoreboardShouldBeUpdated :
        await context.send(">>> **Mise à jour terminée** : Rien à l'horizon !")

@bot.command()
async def createGlobalScoreboard(context):
    """Create a global scoreboard with all players in

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    global globalScoreboardShouldBeUpdated
    global ranking
    global globalScoreboardLaunched
    global lastUpdate

    if globalScoreboardLaunched : 
        await context.send(">>> Le scoreboard se mettra à jour automatiquement d'ici peu")
        return 

    globalScoreboardLaunched = True

    while True : 
        if globalScoreboardShouldBeUpdated :

            ranks = [':one:',':two:',":three:",":four:",":five:",":six:",":seven:",":eight:",":nine:",":keycap_ten:"]

            message = f">>> **Classement général du serveur | {len(ranking.keys())} membres**\n"
            message += f"{lastUpdate}\n"

            scoreboard =  sorted(ranking.items(), key=lambda t: t[1], reverse=True)

            for rank,(username,points) in enumerate(scoreboard) : 
                if rank < 10 :
                    message += f"{ranks[rank]} - **{username}**\n"
                else :
                    message += f"**{rank + 1}** - **{username}**\n"
                message += f"{points} points\n"
            await context.channel.purge(limit=100)
            await context.send(message)
            globalScoreboardShouldBeUpdated = False
        await asyncio.sleep(60)


@bot.command()
async def scoreboard(context):
    """Create a global scoreboard with all players in

    Args:
        context (ctx): the discord channel from where the bot is called
    """

    global ranking
    global ranks
    global lastUpdate

    message = f">>> **Classement général du serveur | {len(ranking.keys())} membres**\n"
    message += f"{lastUpdate}\n"

    scoreboard =  sorted(ranking.items(), key=lambda t: t[1], reverse=True)

    for rank,(username,points) in enumerate(scoreboard) : 
        if rank < 10 :
            message += f"{ranks[rank]} - **{username}**\n"
        else :
            message += f"**{rank + 1}** - **{username}**\n"
        message += f"{points} points\n"

    await context.send(message)






if __name__ == '__main__' :

    # Some variables to handle bruteforcers :(
    alwaysNotifyFlagz = False
    globalScoreboardLaunched = False
    globalScoreboardShouldBeUpdated = False
    lastUpdate = None

    # Display some emojis instead of rank number
    ranks = [':one:',':two:',":three:",":four:",":five:",":six:",":seven:",":eight:",":nine:",":keycap_ten:"]


    # Talks to the database
    pdo = PDO('./db/database.sqlite')
    
    # Talks with root-me user's profiles because their API is kinda shit
    api = API()

    # Generate Notifications Images
    AlwaysUpdate = AlwaysUpdate()

    # Rank users
    ranking = {}

    # Launch
    bot.run(os.getenv("discord_api_key"))