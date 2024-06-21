import sqlite3

class PDO :
    def __init__(self,db) :
        """Initiate an instance of the PDO class to communicate with the database

        Args:
            db (string): the path to the database
        """
        self.db = db
        self.conn = sqlite3.connect(self.db)

    def getUsers(self) : 
        c = self.conn.cursor()
        c.execute("SELECT username FROM Users;")
        users = c.fetchall()
        return users

    def insertUser(self,username) : 
        c = self.conn.cursor()
        try :
            c.execute(f"INSERT INTO Users (username) VALUES ('{username}');")
            self.conn.commit()
            return True 
        except Exception :
            print(Exception)
            return False

    #
    #
    #   Deal with Flagged table
    #
    #
    def getFlagged(self,username) : 
        """Returns all the challenges flagged by the given user

        Args:
            username (str): the username

        Returns:
            list: all the flagged challenges stored in the database
        """
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM Flagged WHERE username='{username}'")
        flagged = c.fetchall()
        return flagged


    def insertFlagged(self,username,challTitle) : 
        """Add a flagged challenge by the given user

        Args:
            username (str): the username
            challTitle (str): the challenge's name

        Returns:
            bool: True if insertion succeeded, false otherwise
        """
        c = self.conn.cursor()
        try :
            c.execute(f"INSERT INTO Flagged (username,title) VALUES ('{username}','{challTitle}');")
            self.conn.commit()
            return True 
        except Exception :
            print(Exception)
            return False

    def getServerRank(self,challengeTitle) : 
        """Returns the number of flag in the server for one given challenge

        Args:
            challengeTitle (str): the challenge name

        Returns:
            int: the rank in the server
        """
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM Flagged WHERE title='{challengeTitle}'")
        resp = c.fetchall()
        return len(resp) + 1

    #
    #
    #   Deal with Autored table
    #
    #
    def getAutored(self,username) : 
        """Returns all the challenges and write-ups autored by the given user

        Args:
            username (str): the username

        Returns:
            list: all the flagged challenges stored in the database
        """
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM Autored WHERE username='{username}'")
        autored = c.fetchall()
        return autored


    def insertAutored(self,username,title) : 
        """Add an autored challenge or write-up by the given user

        Args:
            username (str): the username
            title (str): the challenge's name or write-up's name

        Returns:
            bool: True if insertion succeeded, false otherwise
        """
        c = self.conn.cursor()
        try :
            c.execute(f"INSERT INTO Autored (username,title) VALUES ('{username}','{title}');")
            self.conn.commit()
            return True 
        except Exception :
            print(Exception)
            return False