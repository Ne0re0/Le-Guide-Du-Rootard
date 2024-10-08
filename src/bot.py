#!/usr/bin/python3

import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import os
import re

from dotenv import load_dotenv
from datetime import datetime,timedelta

from local_libs.RootMe.PDO import PDO
from local_libs.RootMe.DiffChecker import DiffChecker
from local_libs.RootMe.API import API
from random import randint

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
    message = ">>> ## **Le-Guide-Du-Rootard --help**\n"
    message += "\n"
    message += "Le guide du rootard saura te mener sur le bonne root\n"
    message += "\n"
    message += "- **/help** : Affiche ce message\n"
    message += "- **/ping** : pong\n"
    message += "- **/pong** : ping\n"
    message += "- **/source** : Affiche l'adresse du code source\n"
    message += "- **/status** : Donne le statut des différentes variables\n"

    message += "\n"
    message += "### **Administration :**\n"
    message += "- **/setAdminChannel** : Défini un salon comme celui dédié à l'administration\n"
    message += "- **/unsetAdminChannel** : Le salon dédié à l'administration redevient un salon classique\n"

    message += "- **/addUser <usernameID>** : Ajoute un utilisateur à la base de données\n"
    message += "- **/removeUser <usernameID>** : Liste les utilisateurs enregistrés\n"
    message += "- **/getUsers** : Liste les utilisateurs enregistrés\n"
    
    message += "- **/enableGlobalNotifications <channelName>** : Défini un salon comme cible pour les notifications de flag\n"
    message += "- **/enableGlobalScoreboard <channelName>** : Crée un scoreboard global qui se mettra à jour automatiquement\n"
    message += "- **/disableGlobalNotifications** : Désactive les notifications globales\n"
    message += "- **/disableGlobalScoreboard** : Désactive le scoreboard global\n"
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


########################################################
###
###        ADMINISTRATION
###
########################################################

@bot.command()
async def status(context):

    print("/status")
    pdo = getPDO(context.guild.id)

    notificationChannel = pdo.getGlobalNotificationsChannelName()
    scoreboardChannel = pdo.getGlobalScoreboardChannelName()
    adminChannel = pdo.getAdminChannelName()
    lastUpdate = pdo.getLastUpdate()
    nextUpdate = pdo.getNextUpdate()

    message = ">>> **Status**\n\n"
    
    if notificationChannel is not None : 
        message += f"**Les notifications de flag apparaissent ici :** {notificationChannel}\n"
    else:
        message += f"**Les notifications de flag sont désactivées**\n"
    
    if scoreboardChannel is not None :
        message += f"**Le scoreboard est mis à jour automatiquement ici :** {scoreboardChannel}\n"
    else :
        message += "**Le scoreboard est désactivé**\n"
    
    if adminChannel is not None :
        message += f"**Le canal d'administration est le suivant :** {adminChannel}\n"
    else :
        message += f"**Le canal d'administration n'est pas établi**\n"

    message += f"**Dernière update :** {lastUpdate}\n"
    message += f"**Prochaine update :** {nextUpdate}\n"

    await context.send(message)

######################################################
###
###               ADMIN CHANNEL
###
######################################################

@bot.command()
async def setAdminChannel(context):
    
    pdo = getPDO(context.guild.id)
    
    print("/setAdminChannel ",end="")

    adminChannelName = pdo.getAdminChannelName()
    adminChannelId = pdo.getAdminChannelId()
    
    if adminChannelId == str(context.channel.id) : 
        await context.send(f"Le canal d'administration est déjà établi dans ce même salon")
        print("FAIL Admin channel is another channel")
        return

    if adminChannelName is not None : 
        print("FAIL Channel already enable")
        await context.send(f"Le canal d'administration est déjà établi dans ce salon : {adminChannelName}")
        return
    
    pdo = getPDO(context.guild.id)
    pdo.setAdminChannelId(context.channel.id)
    pdo.setAdminChannelName(context.channel.name)
    
    adminChannelName = pdo.getAdminChannelName()

    if adminChannelName is None :
        print("FAIL Server Error")
        await context.send(f"Erreur lors de la définition du canal d'administration")
        return
    
    print("SUCCESS")
    await context.send(f"Le canal d'administration a été défini avec succès")



@bot.command()
async def unsetAdminChannel(context):
    
    try :
        assert await isSentFromAdminChannel(context), "/getUsers has not been sent from admin channel"
    except :
        print("/unsetAdminChannel called from a random channel")
        return
    
    print("/unsetAdminChannel ",end="")

    pdo = getPDO(context.guild.id)

    adminChannelName = pdo.getAdminChannelName()
    adminChannelId = pdo.getAdminChannelId()
    
    if adminChannelId is None : 
        print("FAIL Not any admin channel is defined")
        await context.send(f"Aucun canal d'administration n'est défini")
        return

    
    pdo.setAdminChannelName(None)
    pdo.setAdminChannelId(None)
    
    print("SUCCESS Admin channel unset")
    await context.send(f"Canal d'administration désactivé, veuillez l'activer avec /setAdminChannel dans un autre canal pour poursuivre l'administration")

    
######################################################
###
###         PRIVATE METHODS
###
######################################################

async def isSentFromAdminChannel(context) : 
    pdo = getPDO(context.guild.id)

    return str(context.channel.id) == pdo.getAdminChannelId()
        

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
    
    try :
        assert await isSentFromAdminChannel(context), "/getUsers has not been sent from admin channel"
    except :
        print("/getUsers called from a random channel")
        return
    
    print("getUsers")
    pdo = getPDO(context.guild.id)
    users = pdo.getUsers()
    try : 
        if len(users) == 0 :
            message = ">>> Aucun utilisateur enregistré"
        else :
            message = ">>> **Les utilisateurs :**\n\n"
            message += "Format : usernameID:usernameDN\n"

            for user in users : 
                message += f"- {user[0]} : {user[1]}\n"
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

    try :
        assert await isSentFromAdminChannel(context), "/addUser has not been sent from admin channel"
    except :
        print(f"/addUser {usernameID} called from a random channel")
        return
    
    usernameID = usernameID.upper()
    
    if len(usernameID) > 0 :
        print(f"/addUser {usernameID} ",end="")
        res = api.getUser(usernameID)
        timer = 5
        while "status_code" in res.keys() and res["status_code"] != 200 :
            await asyncio.sleep(timer)
            res = api.getUser(usernameID)
            timer += 5

        if "status_code" in res.keys() and res["status_code"] == 404 :
            print("FAIL 404 User does not exist")
            await context.send(f">>> **Utilisateur introuvable** \n\nVérifiez que le nom renseigné est bien celui avec lequel vous accédez au profil public avec https://www.root-me.org/{usernameID}")
            return 

        pdo = getPDO(context.guild.id)
        resp = pdo.insertUser(usernameID,None,None)
        if not resp : 
            print("FAIL User already registered")
            await context.send(">>> **Utilisateur existant**")
            return
        
        # Updating user in the database without notifications

        maj = await diffchecker.update(usernameID,context)
        
        pdo = getPDO(context.guild.id)
        pdo.setGlobalScoreboardShouldBeUpdated("1")

        print("SUCCESS User registered")
        await context.send(f">>> **Utilisateur `{usernameID}`:`{maj['usernameDN']}` ajouté**")


@bot.command()
async def removeUser(context,usernameID):
    """Supprime un utiliateur à la base de données. La casse doit correspondre

    Usage : /addUser usernameID

    Args:
        context (ctx): the discord channel from where the bot is called
        usernameID (string): the usernameID
    """

    try :
        assert await isSentFromAdminChannel(context), "/removeUser has not been sent from admin channel"
    except :
        print(f"/removeUser {usernameID} called from a random channel")
        return
    
    usernameID = usernameID.upper()
    print(f"/removeUser {usernameID} ",end="")
    pdo = getPDO(context.guild.id)
    
    nbUsers = pdo.getNbUsers()
    pdo.deleteUser(usernameID)

    if nbUsers == pdo.getNbUsers() :
        print(f"FAIL User {usernameID} not found in database")
        await context.send(f">>> **Utilisateur `{usernameID}` introuvable**")

    else :
        print(f"SUCCESS {usernameID} deleted")
        pdo.setGlobalScoreboardShouldBeUpdated("1")
        await context.send(f">>> **Utilisateur `{usernameID}` supprimé**")

######################################################
###
###            NOTIFICATION MANAGEMENT
###
######################################################

async def __restartGlobalNotifications(guildId,channelId) :
    guild = await bot.fetch_guild(guildId)
    channel = await guild.fetch_channel(channelId)
    
    pdo = getPDO(channel.guild.id)

    notificationChannelId = channelId
    print("__restartGlobalNotifications")


    while True :
        # Check that the notifying channel has not been changed
        if notificationChannelId != pdo.getGlobalNotificationsChannelId() :
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
        timer = 6200 + randint(-1000,1000)
        
        next_update_time = datetime.now() + timedelta(seconds=timer)    
            
        pdo.setNextUpdate(next_update_time.strftime('%d/%m/%Y %H:%M:%S'))
        await asyncio.sleep(timer)


@bot.command()
async def enableGlobalNotifications(context, channelName):
    """Automatically search for any flag or new information in root-me public profiles of users

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    
    try :
        assert await isSentFromAdminChannel(context), "/enableGlobalNotifications has not been sent from admin channel"
    except :
        print(f"/enableGlobalNotifications called from a random channel")
        return
    
    print("enableGlobalNotifications")
    pdo = getPDO(context.guild.id)
    
    channels = [channel for channel in context.guild.channels if channel.name == channelName]
    
    if len(channels) == 0 :
        await context.send(f">>> Le canal {channelName} n'a pas été trouvé sur ce serveur")
        return
    
    if len(channels) > 1 :
        await context.send(f">>> Plusieurs canaux nommés {channelName} ont été trouvés sur ce serveur, veuillez choisir un canal avec un nom unique")
        return

    channel = channels[0]
    notificationChannelId = pdo.getGlobalNotificationsChannelId()

    if notificationChannelId == str(channel.id) :
        await context.send(f">>> Les notifications sont déjà activées sur le canal {channel.name}")
        return
    elif notificationChannelId != context.channel.id : 
        
        pdo.setGlobalNotificationsChannelId(channel.id)
        pdo.setGlobalNotificationsChannelName(channel.name)
        await context.send(">>> Initialisation des notifications automatiques sur ce canal")

    while True :

        # Check that the notifying channel has not been changed
        if pdo.getGlobalNotificationsChannelId() != str(channel.id) :
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
                    await channel.send(file=picture)
                os.remove(img)

        pdo.setLastUpdate(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        timer = 6200 + randint(-1000,1000)
        
        timerAnd5Min = timer + 5*60
        next_update_time = datetime.now() + timedelta(seconds=timerAnd5Min)    
            
        pdo.setNextUpdate(next_update_time.strftime('%d/%m/%Y %H:%M:%S'))
        await asyncio.sleep(timer)


@bot.command()
async def disableGlobalNotifications(context):
    
    try :
        assert await isSentFromAdminChannel(context), "/disableGlobalNotifications has not been sent from admin channel"
    except :
        print(f"/disableGlobalNotifications called from a random channel")
        return
    
    pdo = getPDO(context.guild.id)
    channelId = pdo.getGlobalNotificationsChannelId()
    if channelId is None : 
        await context.send(">>> Les notifications globales sont déjà désactivées")

    else :
        pdo.setGlobalNotificationsChannelId(None)
        pdo.setGlobalNotificationsChannelName(None)
        await context.send(">>> Notifications automatiques désactivées")


######################################################
###
###              SCOREBOARD MANAGEMENT
###
######################################################

async def __restartGlobalScoreboard(guildId,channelId) :
    guild = await bot.fetch_guild(guildId)
    channel = await guild.fetch_channel(channelId)

    global ranks
    pdo = getPDO(channel.guild.id)
    globalScoreboardChannelId = channelId
    print("__restartGlobalScoreboard")


    while True : 

        if pdo.getGlobalScoreboardChannelId() != globalScoreboardChannelId and pdo.getGlobalScoreboardChannelId() is not None :
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
                        message += f"{ranks[rank]} - **{re.escape(usernameDN).replace("\\ ", " ")}**\n"
                    else :
                        message += f"**{rank + 1}** - **{re.escape(usernameDN).replace("\\ ", " ")}**\n"
                    message += f"{points} points\n"

                await channel.purge(limit=None)
                await channel.send(message)

            pdo.setGlobalScoreboardShouldBeUpdated("0")
        await asyncio.sleep(60)
    

@bot.command()
async def enableGlobalScoreboard(context, channelName):
    """Create a global scoreboard with all players in and enable auto-update

    Args:
        context (ctx): the discord channel from where the bot is called
    """
    
    try :
        assert await isSentFromAdminChannel(context), "/enableGlobalScoreboard has not been sent from admin channel"
    except :
        print(f"/enableGlobalScoreboard called from a random channel")
        return

    print("createGlobalScoreboard")
    
    global ranks
    pdo = getPDO(context.guild.id)
    globalScoreboardLaunched = pdo.getGlobalScoreboardChannelId()
    
    channels = [channel for channel in context.guild.channels if channel.name == channelName]
    
    if len(channels) == 0 :
        await context.send(f">>> Le canal {channelName} n'a pas été trouvé sur ce serveur")
        return
    
    if len(channels) > 1 :
        await context.send(f">>> Plusieurs canaux nommés {channelName} ont été trouvés sur ce serveur, veuillez choisir un canal avec un nom unique")
        return
    
    channel = channels[0]
    
    # Case channel is the same
    if globalScoreboardLaunched == str(channel.id) :
        await context.send(f">>> Le scoreboard est déjà établi sur le canal {channel.name}")
        return
    # Case channel move
    else : 
        pdo.setGlobalScoreboardChannelId(channel.id)
        pdo.setGlobalScoreboardChannelName(channel.name)
        pdo.setGlobalScoreboardShouldBeUpdated("1")
        await context.send(f">>> Le scoreboard a été initialisé sur le canal {channel.name}")


    while True : 
        
        if pdo.getGlobalScoreboardChannelId() != str(channel.id) and pdo.getGlobalScoreboardChannelId() is not None :
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
                        message += f"{ranks[rank]} - **{re.escape(usernameDN).replace("\\ ", " ")}**\n"
                    else :
                        message += f"**{rank + 1}** - **{re.escape(usernameDN).replace("\\ ", " ")}**\n"
                    message += f"{points} points\n"

                await channel.purge(limit=None)
                await channel.send(message)

            pdo.setGlobalScoreboardShouldBeUpdated("0")
        await asyncio.sleep(60)


@bot.command()
async def disableGlobalScoreboard(context):
    
    try :
        assert await isSentFromAdminChannel(context), "/disableGlobalScoreboard has not been sent from admin channel"
        print(f"/disableGlobalScoreboard")
    except :
        print(f"/disableGlobalScoreboard called from a random channel")
        return

    pdo = getPDO(context.guild.id)
    channelId = pdo.getGlobalScoreboardChannelId()
    if channelId is None :
        await context.send(">>> Le scoreboard global n'est pas activé")

    else :
        pdo.setGlobalScoreboardChannelId(None)
        pdo.setGlobalScoreboardChannelName(None)
        await context.send(">>> Scoreboard automatique désactivé")


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