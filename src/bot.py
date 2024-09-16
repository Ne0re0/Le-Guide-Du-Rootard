#!/usr/bin/python3

import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

from local_libs.RootMe.PDO import PDO
from local_libs.RootMe.DiffChecker import DiffChecker
from local_libs.RootMe.API import API

load_dotenv()

bot = commands.Bot(command_prefix="/", description="Le guide du rootard", intents=discord.Intents.all())

def getPDO(guildId) : 
    global PDOs
    if guildId in PDOs.keys() :
        pdo = PDOs[guildId]
    else :
        pdo = PDO(guildId)
        PDOs[guildId] = pdo
    return pdo

@bot.event
async def on_ready():
    await start()
    print("Bot ready !")

bot.remove_command("help")
@bot.command()
async def help(context):
    message = ">>> ## **Au secours**\n"
    message += "\n"
    message += "Le guide du rootard saura te mener sur le bonne root\n"
    message += "\n"
    message += "- **/help** : Affiche ce message\n"
    message += "- **/ping** : pong\n"
    message += "- **/pong** : ping\n"
    message += "- **/source** : Affiche l'adresse du code source\n"
    message += "- **/status** : Donne le statut des différentes variables\n"
    message += "- **/getUsers** : Liste les utilisateurs enregistrés\n"
    message += "- **/addUser usernameID** : Ajoute un utilisateur à la base de données\n"
    message += "- **/enableGlobalNotifications** : Défini un salon comme cible pour les notifications de flag\n"
    message += "- **/enableGlobalScoreboard** : Crée un scoreboard global qui se mettra à jour automatiquement\n"
    message += "- **/update** : Met à jour chaque utilisateur avec les informations de root-me\n"
    message += "- **/scoreboard** : Affiche le scoreboard\n"
    message += "\n"
    await context.send(message)


@bot.command()
async def ping(context):
    await context.send(">>> pong")

@bot.command()
async def pong(context):
    await context.send(">>> ping")

@bot.command()
async def source(context):
    await context.send(">>> **https://github.com/Ne0re0/Le-Guide-Du-Rootard**")

@bot.command()
async def status(context):

    pdo = getPDO(context.guild.id)

    alwaysNotifyFlagz = pdo.getGlobalNotificationsChannelName()
    globalScoreboardLaunched = pdo.getGlobalScoreboardChannelName()
    globalScoreboardShouldBeUpdated = pdo.getGlobalScoreboardShouldBeUpdated()
    lastUpdate = pdo.getLastUpdate()

    message = ">>> **Status**\n\n"
    message += f"**Notifier lors d'un flag :** {alwaysNotifyFlagz}\n"
    message += f"**Le scoreboard est mis à jour automatiquement :** {globalScoreboardLaunched}\n"
    message += f"**Le scoreboard doit va être mis à jour prochainement :** {globalScoreboardShouldBeUpdated == '1'}\n"
    message += f"**Dernière update :** {lastUpdate}\n"

    await context.send(message)


######################################################
###
###               RESTART MANAGEMENT
###
######################################################

async def start():
    """
       This function will restart Global Notifications 
       and Global Scoreboard after the bot went down.
    """

    # If no db then there is nothing to restart
    if not os.path.exists('db') or len([file for file in os.listdir("db") if file.endswith('.sqlite')]) == 0:
        print("Nothing to restart")
        return

    dbs = [file for file in os.listdir("db") if file.endswith('.sqlite')]
    for db in dbs :
        print(f"Restarting {db}")
        serverId = db.split(".")[0]
        pdo = getPDO(serverId) # Retrieve the discord server id
        globalNotificationsChannelId = pdo.getGlobalNotificationsChannelId()
        globalScoreboardChannelId = pdo.getGlobalScoreboardChannelId()

        if globalNotificationsChannelId is not None :
            asyncio.create_task(__restartGlobalNotifications(serverId,globalNotificationsChannelId))

        if globalScoreboardChannelId is not None :
            asyncio.create_task(__restartGlobalScoreboard(serverId,globalScoreboardChannelId))



######################################################
###
###               USERS MANAGEMENT
###
######################################################

@bot.command()
async def getUsers(context):
    print("getUsers")
    pdo = getPDO(context.guild.id)
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
        print("addUser")
        res = api.getUser(usernameID)
        timer = 5
        while "status_code" in res.keys() and res["status_code"] != 200 :
            await asyncio.sleep(timer)
            res = api.getUser(usernameID)
            timer += 5

        if "status_code" in res.keys() and res["status_code"] == 404 :
            await context.send(f">>> **Utilisateur introuvable** \n\nVérifiez que le nom renseigné est bien celui avec lequel vous accédez au profil public avec https://www.root-me.org/{usernameID}")
            return 

        pdo = getPDO(context.guild.id)
        resp = pdo.insertUser(usernameID,None,None)
        if not resp : 
            await context.send(">>> **Utilisateur existant**")
            return
        
        # Updating user in the database without notifications

        maj = await diffchecker.update(usernameID,context)
        
        pdo = getPDO(context.guild.id)
        pdo.setGlobalScoreboardShouldBeUpdated("1")

        await context.send(f">>> **Utilisateur `{usernameID}`:`{maj['usernameDN']}` ajouté**")

######################################################
###
###            NOTIFICATION MANAGEMENT
###
######################################################

async def __restartGlobalNotifications(guildId,channelId) :
    guild = await bot.fetch_guild(guildId)
    channel = await guild.fetch_channel(channelId)
    # await channel.send(">>> Redémarrage des notifications globales")
    
    pdo = getPDO(channel.guild.id)

    alwaysNotifyFlagz = channelId

    while True :
        print("__restartGlobalNotifications")
        # Check that the notifying channel has not been changed
        if alwaysNotifyFlagz != pdo.getGlobalNotificationsChannelId() :
            return

        for user in pdo.getUsers() : 
            usernameID = user[0]

            print(f'Looking for {usernameID}')

            maj = await diffchecker.update(usernameID,channel)
            
            for img in maj["images"] :
                pdo.setGlobalScoreboardShouldBeUpdated("1")
                with open(img ,'rb') as f:
                    picture = discord.File(f)
                    await channel.send(file=picture)
                os.remove(img)

        pdo.setLastUpdate(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        await asyncio.sleep(7200) # 2h


@bot.command()
async def enableGlobalNotifications(context):
    """Automatically search for any flag or new information in root-me public profiles of users

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    print("enableGlobalNotifications")
    pdo = getPDO(context.guild.id)

    alwaysNotifyFlagz = pdo.getGlobalNotificationsChannelId()

    if alwaysNotifyFlagz == str(context.channel.id) :
        await context.send(">>> Les notifications sont déjà activées sur ce canal")
        return
    elif alwaysNotifyFlagz != context.channel.id : 
        pdo.setGlobalNotificationsChannelId(context.channel.id)
        pdo.setGlobalNotificationsChannelName(context.channel.name)
        await context.send(">>> Initialisation des notifications automatiques sur ce canal")

    while True :

        # Check that the notifying channel has not been changed
        if pdo.getGlobalNotificationsChannelId() != str(context.channel.id) :
            channelName = pdo.getGlobalNotificationsChannelName()
            await context.send(f">>> Le scoreboard a été déplacé dans le canal suivant : {channelName}")
            return

        # Starts the update
        pdo.setLastUpdate("En cours")
        for user in pdo.getUsers() : 
            usernameID = user[0]

            print(f'{usernameID} ',end=" ")

            maj = await diffchecker.update(usernameID,context)
            
            for img in maj["images"] :
                pdo.setGlobalScoreboardShouldBeUpdated("1")
                with open(img ,'rb') as f:
                    picture = discord.File(f)
                    await context.send(file=picture)
                os.remove(img)

        print("\n")
        pdo.setLastUpdate(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        await asyncio.sleep(7200) # 2h


@bot.command()
async def disableGlobalNotifications(context):
    pdo = getPDO(context.guild.id)
    channelId = pdo.getGlobalNotificationsChannelId()
    if channelId is None : 
        await context.send(">>> Les notifications globales sont déjà désactivées")

    if channelId != str(context.channel.id) :
        channelName = pdo.getGlobalNotificationsChannelName()
        await context.send(f">>> Vous devez saisir la commande /disableGlobalNotifications dans le canal {channelName}")

    else :
        pdo.setGlobalNotificationsChannelId(None)
        pdo.setGlobalNotificationsChannelName(None)
        await context.send(">>> Notifications automatiques désactivées")


@bot.command()
async def update(context):
    """Search for any flag or new information in root-me public profiles of users

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    print("update")
    pdo = getPDO(context.guild.id)
    changes = False

    await context.send(">>> **Recherche de mises à jour**")

    os.system('echo "Last run : $(date)" >> /tmp/logs.txt')
    pdo = getPDO(context.guild.id)
    for user in pdo.getUsers() : 
        usernameID = user[0]

        print(f'{usernameID}',end=" ")

        maj = await diffchecker.update(usernameID,context)
        
        for img in maj["images"] :
            changes = True
            pdo.setGlobalScoreboardShouldBeUpdated("1")
            with open(img ,'rb') as f:
                picture = discord.File(f)
                await context.send(file=picture)
            os.remove(img)
    print()

    if not changes : 
        await context.send(">>> Aucune mise à jour n'a été trouvée")

    pdo.setLastUpdate(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))


######################################################
###
###              SCOREBOARD MANAGEMENT
###
######################################################

async def __restartGlobalScoreboard(guildId,channelId) :
    guild = await bot.fetch_guild(guildId)
    channel = await guild.fetch_channel(channelId)
    await channel.send(">>> Redémarrage du scoreboard global")

    global ranks
    pdo = getPDO(channel.guild.id)
    globalScoreboardChannelId = channelId

    while True : 
        print("__restartGlobalScoreboard")

        if pdo.getGlobalScoreboardChannelId() != globalScoreboardChannelId and pdo.getGlobalScoreboardChannelId() is not None :
            channelName = pdo.getGlobalScoreboardChannelName()
            await channel.send(f">>> Le scoreboard a été déplacé dans le canal suivant : {channelName}")
            return

        if pdo.getGlobalScoreboardShouldBeUpdated() == "1":

            users = pdo.getUsers()

            if len(users) == 0 :
                await channel.send(">>> Aucun utilisateur enregistré")
                
            else :
                message = f">>> **Classement général du serveur | {len(users)} membres**\n"
                message += f"{pdo.getLastUpdate()}\n"

                scoreboard =  sorted(users, key=lambda t: t[2], reverse=True)

                for rank,(usernameID,usernameDN,points) in enumerate(scoreboard) : 
                    if rank < len(ranks) :
                        message += f"{ranks[rank]} - **{usernameDN}**\n"
                    else :
                        message += f"**{rank + 1}** - **{usernameDN}**\n"
                    message += f"{points} points\n"

                await channel.purge(limit=None)
                await channel.send(message)

            pdo.setGlobalScoreboardShouldBeUpdated("0")
        await asyncio.sleep(60)
    

@bot.command()
async def enableGlobalScoreboard(context):
    """Create a global scoreboard with all players in and enable auto-update

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    print("createGlobalScoreboard")
    
    global ranks
    pdo = getPDO(context.guild.id)
    globalScoreboardLaunched = pdo.getGlobalScoreboardChannelId()
    
    # Case channel is the same
    if globalScoreboardLaunched == str(context.channel.id) :
        await context.send(">>> Le scoreboard se mettra à jour automatiquement d'ici peu sur ce canal")
        return
    # Case channel move
    elif globalScoreboardLaunched != context.channel.id : 
        pdo.setGlobalScoreboardChannelId(context.channel.id)
        pdo.setGlobalScoreboardChannelName(context.channel.name)
        pdo.setGlobalScoreboardShouldBeUpdated("1")
        await context.send(">>> Le scoreboard a été initialisé sur ce canal")


    while True : 
        
        if pdo.getGlobalScoreboardChannelId() != str(context.channel.id) and pdo.getGlobalScoreboardChannelId() is not None :
            channelName = pdo.getGlobalScoreboardChannelName()
            await context.send(f">>> Le scoreboard a été déplacé dans le canal suivant : {channelName}")
            return

        if pdo.getGlobalScoreboardShouldBeUpdated() == "1":

            users = pdo.getUsers()

            if len(users) == 0 :
                await context.send(">>> Aucun utilisateur enregistré")
                
            else :
                message = f">>> **Classement général du serveur | {len(users)} membres**\n"
                message += f"{pdo.getLastUpdate()}\n"

                scoreboard =  sorted(users, key=lambda t: t[2], reverse=True)

                for rank,(usernameID,usernameDN,points) in enumerate(scoreboard) : 
                    if rank < len(ranks) :
                        message += f"{ranks[rank]} - **{usernameDN}**\n"
                    else :
                        message += f"**{rank + 1}** - **{usernameDN}**\n"
                    message += f"{points} points\n"

                await context.channel.purge(limit=None)
                await context.send(message)

            pdo.setGlobalScoreboardShouldBeUpdated("0")
        await asyncio.sleep(60)


@bot.command()
async def disableGlobalScoreboard(context):
    pdo = getPDO(context.guild.id)
    channelId = pdo.getGlobalScoreboardChannelId()
    if channelId is None :
        await context.send(">>> Le scoreboard global n'est pas activé")

    elif channelId != str(context.channel.id) :
        channelName = pdo.getGlobalScoreboardChannelName()
        await context.send(f">>> Vous devez saisir la commande /disableGlobalScoreboard dans le canal {channelName}")

    else :
        pdo.setGlobalScoreboardChannelId(None)
        pdo.setGlobalScoreboardChannelName(None)
        await context.send(">>> Scoreboard automatique désactivé")


@bot.command()
async def scoreboard(context):
    """Display the scoreboard

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    print("scoreboard")

    global ranks

    pdo = getPDO(context.guild.id)

    users = pdo.getUsers()

    if len(users) == 0 :
        await context.send(">>> Aucun utilisateur enregistré")
        return

    message = f">>> **Classement général du serveur | {len(users)} membres**\n"
    message += f"{pdo.getLastUpdate()}\n"

    scoreboard =  sorted(users, key=lambda t: t[2], reverse=True)
    
    for rank,(usernameID,usernameDN,points) in enumerate(scoreboard) : 
        if rank < len(ranks) :
            message += f"{ranks[rank]} - **{usernameDN}**\n"
        else :
            message += f"**{rank + 1}** - **{usernameDN}**\n"
        message += f"{points} points\n"
    await context.send(message)


if __name__ == '__main__' :

    # Used to open and use only one database socket at the time for each discord server 
    PDOs = {}

    # Display some emojis instead of rank number
    ranks = [':first_place:',':second_place:',":third_place:",":four:",":five:",":six:",":seven:",":eight:",":nine:",":keycap_ten:"]

    # Talks with root-me user's profiles because their API is kinda shit
    api = API()

    # Generate Notifications Images
    diffchecker = DiffChecker()

    # Launch
    bot.run(os.getenv("discord_api_key"))