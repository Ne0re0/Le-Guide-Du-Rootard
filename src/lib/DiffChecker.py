#!/bin/python

from lib.PDO import PDO
from lib.API import API
from lib.IMG import IMG
from PIL import Image
import string
import random
import asyncio

class DiffChecker:
        
    def getDiff(self,apidata,pdodataFlagz,pdodataContributions,pdo,usernameID) :

        diff = {"challenges": [], "contributions": {"challenges" : [], "solutions": []}}
        pdo.updateUsersPoints(usernameID,apidata['points'])
        pdo.updateUsersDN(usernameID,apidata['username'])

        alreadyFlaggedChallenges = [row[1] for row in pdodataFlagz]
        alreadyAutoredChallenges = [row[1] for row in pdodataContributions]

        for challenge in apidata["recentActivity"] : 
            if challenge["name"] not in alreadyFlaggedChallenges :
                diff["challenges"].append(challenge)
                pdo.insertFlagged(usernameID,challenge["name"])
        
        for challenge in apidata["contributions"]["challenges"] : 
            if challenge["title"] not in alreadyAutoredChallenges :
                diff["contributions"]["challenges"].append(challenge)
                pdo.insertAutored(usernameID,challenge["title"])
        
        for challenge in apidata["contributions"]["solutions"] : 
            if challenge["title"] not in alreadyAutoredChallenges :
                diff["contributions"]["solutions"].append(challenge)
                pdo.insertAutored(usernameID,challenge["title"])

        return diff


    def get_random_string(self,length):
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str


    async def update(self,usernameID,context) :
        api = API()
        pdo = PDO(context.guild.id)
        img_generator = IMG()
        images = []

        apidata = api.getUser(usernameID)
        timer = 5
        while "status_code" in apidata.keys() : 
            print(f'Status code {apidata["status_code"]}, retrying in {timer} seconds')
            apidata = api.getUser(usernameID)
            await asyncio.sleep(timer)
            timer += 5


        pdodataFlagz = pdo.getFlagged(usernameID)
        pdodataContributions = pdo.getAutored(usernameID)

        diff = self.getDiff(apidata,pdodataFlagz,pdodataContributions,pdo,usernameID)

        # generate images for new challenges solved
        for challenge in diff["challenges"] : 
            img = img_generator.generateImage(
                "NOUVEAU FLAG",
                apidata['username'],
                apidata["profilePicture"].split("?")[0],
                apidata["points"],
                challenge["name"],
                challenge["category"],
                challenge["logo"].split("?")[0],
                pdo.getServerRank(challenge["name"])
            )
            filename = self.get_random_string(20)
            img.save(f"/tmp/{filename}.png")
            images.append(f"/tmp/{filename}.png")
        
        # Generate images for new challenges added to rootme
        for challenge in diff["contributions"]["challenges"] : 
            img = img_generator.generateImage(
                "NOUVEAU CHALLENGE CREE",
                apidata['username'],
                apidata["profilePicture"].split("?")[0],
                apidata["points"],
                challenge["title"],
                challenge["category"],
                challenge["logo"].split("?")[0],
                None
            )
            filename = self.get_random_string(20)
            img.save(f"/tmp/{filename}.png")
            images.append(f"/tmp/{filename}.png")
        
        # Generate images for new write-ups added to rootme
        for challenge in diff["contributions"]["solutions"] : 
            img = img_generator.generateImage(
                "NOUVEAU WRITE-UP CREE",
                apidata['username'],
                apidata["profilePicture"].split("?")[0],
                apidata["points"],
                challenge["title"],
                challenge["category"],
                challenge["logo"].split("?")[0],
                None
            )
            filename = self.get_random_string(20)
            img.save(f"/tmp/{filename}.png")
            images.append(f"/tmp/{filename}.png")
    
        return {"usernameDN" : apidata['username'], "points" : apidata["points"], "images" :images}


        
