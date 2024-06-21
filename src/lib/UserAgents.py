from random import choice

class UserAgents :

    def __init__(self,filepath) : 
        self.filepath = filepath
        with open(filepath,"r") as f :
            self.usersAgents = f.read().split("\n")[:-1]

    def getRandom(self) : 
        return choice(self.usersAgents)

