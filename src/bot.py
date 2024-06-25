#!/usr/bin/python3

import discord
from discord.ext import commands
import asyncio
import os
from lib.PDO import PDO
from lib.DiffChecker import DiffChecker
import os
from dotenv import load_dotenv
from datetime import datetime
from lib.API import API

load_dotenv()

bot = commands.Bot(command_prefix="/", description="Le guide du routard", intents=discord.Intents.all())


def getPDO(context) : 
    global PDOs

    if context.guild.id in PDOs.keys() :
        pdo = PDOs[context.guild.id]
    else :
        pdo = PDO(context.guild.id)
        PDOs[context.guild.id] = pdo
    return pdo


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
    message += "- **/source** : Affiche l'adresse du code source"
    message += "- **/status** : Donne le statut des différentes variables"
    message += "- **/getUsers** : Liste les utilisateurs enregistrés"
    message += "- **/addUser usernameID** : Ajoute un utilisateur à la base de données"
    message += "- **/enableGlobalNotifications** : Défini un salon comme cible pour les notifications de flag"
    message += "- **/createGlobalScoreboard** : Crée un scoreboard global qui se mettra à jour automatiquement"
    message += "- **/update** : Met à jour chaque utilisateur avec les informations de root-me"
    message += "- **/scoreboard** : Affiche le scoreboard"
    message += "\n"
    await context.send(message)


@bot.command()
async def ping(context):
    await context.send(">>> pong")

# @bot.command()
# async def test(context):
#     print(context.guild.id)


@bot.command()
async def pong(context):
    await context.send(">>> ping")

@bot.command()
async def source(context):
    await context.send(">>> **https://github.com/Ne0re0/Le-Guide-Du-Rootard**")


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
    pdo = getPDO(context)
    users = pdo.getUsers()
    try : 
        if len(users) == 0 :
            message = ">>> Aucun utilisateur enregistré"
        else :
            message = ">>> **Les utilisateurs :**\n\n"
            for user in users : 
                message += f"- {user[0]} : {user[2]}\n"
    except Exception :
        message = ">>> Une erreur est survenue"

    await context.send(message)



@bot.command()
async def addUser(context,usernameID):
    """Ajoute un utiliateur à la base de données. La casse doit correspondre

    Usage : /addUser usernameID

    Args:
        context (ctx): the discord channel from where the bot is called
        usernameID (string): the usernameID
    """
    if len(usernameID) > 0 :
        
        res = api.getUser(usernameID)
        timer = 5
        while "status_code" in res.keys() and res["status_code"] == 429 :
            await asyncio.sleep(timer)
            res = api.getUser(usernameID)
            timer += 5

        if "status_code" in res.keys() and res["status_code"] == 404 :
            await context.send(f">>> **Utilisateur introuvable** \n\nVérifiez que le nom renseigné est bien celui avec lequel vous accédez au profil public avec https://www.root-me.org/{usernameID}")
            return 

        pdo = getPDO(context)
        resp = pdo.insertUser(usernameID,None,None)
        if not resp : 
            await context.send(">>> **Utilisateur existant**")
            return
        
        # Updating user in the database without notifications

        global globalScoreboardShouldBeUpdated

        maj = await diffchecker.update(usernameID,context)
        
        globalScoreboardShouldBeUpdated = True

        await context.send(f">>> **Utilisateur `{usernameID}`:`{maj['usernameDN']}` ajouté**")



@bot.command()
async def enableGlobalNotifications(context):
    """Automatically search for any flag or new information in root-me public profiles of users

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    global alwaysNotifyFlagz
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
        pdo = getPDO(context)
        for user in pdo.getUsers() : 
            usernameID = user[0]

            print(f'Looking for {usernameID}')

            maj = await diffchecker.update(usernameID,context)
            
            for img in maj["images"] :
                globalScoreboardShouldBeUpdated = True
                with open(img ,'rb') as f:
                    picture = discord.File(f)
                    await context.send(file=picture)
                os.remove(img)

        lastUpdate = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        print("end")
        await asyncio.sleep(7200) # 2h





@bot.command()
async def update(context):
    """Search for any flag or new information in root-me public profiles of users

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    global alwaysNotifyFlagz
    global globalScoreboardShouldBeUpdated
    global lastUpdate

    await context.send(">>> **Recherche de mises à jour**")

    print("running")
    os.system('echo "Last run : $(date)" >> /tmp/logs.txt')
    pdo = getPDO(context)
    for user in pdo.getUsers() : 
        usernameID = user[0]

        print(f'Looking for {usernameID}')

        maj = await diffchecker.update(usernameID,context)
        
        for img in maj["images"] :
            globalScoreboardShouldBeUpdated = True
            with open(img ,'rb') as f:
                picture = discord.File(f)
                await context.send(file=picture)
            os.remove(img)

    lastUpdate = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print("end")




@bot.command()
async def createGlobalScoreboard(context):
    """Create a global scoreboard with all players in and enable auto-update

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    global globalScoreboardShouldBeUpdated
    global globalScoreboardLaunched
    global lastUpdate

    if globalScoreboardLaunched : 
        await context.send(">>> Le scoreboard se mettra à jour automatiquement d'ici peu")
        return 

    globalScoreboardLaunched = True
    await context.send(">>> Activation du scoreboard global dans ce canal")

    pdo = getPDO(context)

    while True : 
        if globalScoreboardShouldBeUpdated :

            global ranks

            users = pdo.getUsers()

            if len(users) == 0 :
                await context.send(">>> Aucun utilisateur enregistré")
                return
            print(users)
            message = f">>> **Classement général du serveur | {len(users)} membres**\n"
            message += f"{lastUpdate}\n"

            scoreboard =  sorted(users, key=lambda t: t[2], reverse=True)

            for rank,(usernameID,usernameDN,points) in enumerate(scoreboard) : 
                if rank < len(ranks) :
                    message += f"{ranks[rank]} - **{usernameDN}**\n"
                else :
                    message += f"**{rank + 1}** - **{usernameDN}**\n"
                message += f"{points} points\n"

            await context.channel.purge(limit=100)
            await context.send(message)
            globalScoreboardShouldBeUpdated = False
        await asyncio.sleep(60)


@bot.command()
async def scoreboard(context):
    """Display the scoreboard

    Args:
        context (ctx): the discord channel from where the bot is called
    """

    global ranks
    global lastUpdate

    pdo = getPDO(context)

    users = pdo.getUsers()

    if len(users) == 0 :
        await context.send(">>> Aucun utilisateur enregistré")
        return

    message = f">>> **Classement général du serveur | {len(users)} membres**\n"
    message += f"{lastUpdate}\n"

    scoreboard =  sorted(users, key=lambda t: t[2], reverse=True)
    
    for rank,(usernameID,usernameDN,points) in enumerate(scoreboard) : 
        if rank < len(ranks) :
            message += f"{ranks[rank]} - **{usernameDN}**\n"
        else :
            message += f"**{rank + 1}** - **{usernameDN}**\n"
        message += f"{points} points\n"

    await context.send(message)





if __name__ == '__main__' :

    # Some variables to handle bruteforcers :(
    alwaysNotifyFlagz = False
    globalScoreboardLaunched = False
    globalScoreboardShouldBeUpdated = True
    lastUpdate = None

    PDOs = {}

    # Display some emojis instead of rank number
    ranks = [':first_place:',':second_place:',":third_place:",":four:",":five:",":six:",":seven:",":eight:",":nine:",":keycap_ten:"]

    # Talks with root-me user's profiles because their API is kinda shit
    api = API()

    # Generate Notifications Images
    diffchecker = DiffChecker()

    # Rank users
    ranking = {}

    # Launch
    bot.run(os.getenv("discord_api_key"))