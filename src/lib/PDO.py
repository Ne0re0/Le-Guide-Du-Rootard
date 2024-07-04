import sqlite3
import os

def create_db(path):
    try:
        # Connect to the SQLite database specified by the path
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        print("Connected to database successfully")

        # SQL commands to create the tables
        create_users_table = '''
        CREATE TABLE IF NOT EXISTS Users (
            usernameID TEXT PRIMARY KEY, -- Unique username
            usernameDN TEXT, -- Display username
            points INTEGER
        );
        '''

        create_autored_table = '''
        CREATE TABLE IF NOT EXISTS Autored (
            username TEXT,
            title TEXT,
            category TEXT,
            type TEXT,
            PRIMARY KEY (username, title, category, type),
            FOREIGN KEY (username) REFERENCES Users(usernameID)
        );
        '''

        create_flagged_table = '''
        CREATE TABLE IF NOT EXISTS Flagged (
            username TEXT,
            title TEXT,
            category TEXT,
            PRIMARY KEY (username, title, category),
            FOREIGN KEY (username) REFERENCES Users(usernameID)
        );
        '''

        create_information_table = '''
        CREATE TABLE IF NOT EXISTS Informations (
            key TEXT,
            value TEXT,
            PRIMARY KEY (key)
        );
        '''

        # Execute the SQL commands to create the tables
        cursor.execute(create_users_table)
        cursor.execute(create_autored_table)
        cursor.execute(create_flagged_table)
        cursor.execute(create_information_table)

        # Insert initial values into Informations table
        initial_data = [
            ('globalScoreboardChannelId', None),
            ('globalScoreboardChannelName', None),
            ('globalNotificationsChannelId', None),
            ('globalNotificationsChannelName', None),
            ('globalScoreboardShouldBeUpdated', "1"),
            ('lastUpdate', None)
        ]
        cursor.executemany('INSERT OR IGNORE INTO Informations (key, value) VALUES (?, ?);', initial_data)

        # Commit the changes and close the connection
        conn.commit()

        os.system(f"/bin/chmod 666 {path}")

        print(f"Database {path} created")

    except sqlite3.Error as error:
        print(f"Error while creating a sqlite table: {error}")

    finally:
        if conn:
            conn.close()


class PDO:
    def __init__(self, db):
        """Initiate an instance of the PDO class to communicate with the database

        Args:
            db (string): the path to the database
        """
        self.db = db
        self.path = f"db/{self.db}.sqlite"

        if not os.path.exists('db'):
            os.makedirs('db')
        
        if not os.path.exists(self.path):
            create_db(self.path)

        self.conn = sqlite3.connect(self.path)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def getUsers(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Users;")
        users = c.fetchall()
        return users

    def insertUser(self, usernameID, usernameDN, points):
        c = self.conn.cursor()
        try:
            c.execute("INSERT INTO Users (usernameID, usernameDN, points) VALUES (?, ?, ?);", (usernameID, usernameDN, points))
            self.conn.commit()
            return True 
        except sqlite3.Error as e:
            print(f"Exception in insertUser: {e}")
            return False
    
    def updateUsersPoints(self, usernameID, points):
        c = self.conn.cursor()
        try:
            c.execute("UPDATE Users SET points=? WHERE usernameID=?;", (points, usernameID))
            self.conn.commit()
            return True 
        except sqlite3.Error as e:
            print(f"Exception in updateUsersPoints: {e}")
            return False

    def updateUsersDN(self, usernameID, usernameDN):
        c = self.conn.cursor()
        try:
            c.execute("UPDATE Users SET usernameDN=? WHERE usernameID=?;", (usernameDN, usernameID))
            self.conn.commit()
            return True 
        except sqlite3.Error as e:
            print(f"Exception in updateUsersDN: {e}")
            return False

    #
    #
    #   Deal with Flagged table
    #
    #

    def getFlagged(self, username):
        """Returns all the challenges flagged by the given user

        Args:
            username (str): the username

        Returns:
            list: all the flagged challenges stored in the database
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM Flagged WHERE username=?;", (username,))
        flagged = c.fetchall()
        return flagged

    def insertFlagged(self, username, challTitle, category):
        """Add a flagged challenge by the given user

        Args:
            username (str): the username
            challTitle (str): the challenge's name
            category (str): the challenge's category

        Returns:
            bool: True if insertion succeeded, false otherwise
        """
        c = self.conn.cursor()
        try:
            c.execute("INSERT INTO Flagged (username, title, category) VALUES (?, ?, ?);", (username, challTitle, category))
            self.conn.commit()
            return True 
        except sqlite3.Error as e:
            print(f"Exception in insertFlagged: {e}")
            return False


    #
    #
    #   Deal with Autored table
    #
    #
    def getAutored(self, username):
        """Returns all the challenges and write-ups autored by the given user

        Args:
            username (str): the username

        Returns:
            list: all the autored challenges and write-ups stored in the database
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM Autored WHERE username=?;", (username,))
        autored = c.fetchall()
        return autored

    def insertAutored(self, username, title, category, type):
        """Add an autored challenge or write-up by the given user

        Args:
            username (str): the username
            title (str): the challenge's name or write-up's name

        Returns:
            bool: True if insertion succeeded, false otherwise
        """
        c = self.conn.cursor()
        try:
            c.execute("INSERT INTO Autored (username, title, category, type) VALUES (?, ?, ?, ?);", (username, title, category, type))
            self.conn.commit()
            return True 
        except sqlite3.Error as e:
            print(f"Exception in insertAutored: {e}")
            return False

    #
    #
    # Deal with information table
    #
    #

    def getGlobalScoreboardChannelId(self):
        c = self.conn.cursor()
        c.execute('SELECT value FROM Informations WHERE key = ?', ('globalScoreboardChannelId',))
        result = c.fetchone()
        return result[0] if result else None

    def setGlobalScoreboardChannelId(self, value):
        c = self.conn.cursor()
        c.execute("UPDATE Informations SET value = ? WHERE key='globalScoreboardChannelId';", (value,))
        self.conn.commit()

    def getGlobalScoreboardChannelName(self):
        c = self.conn.cursor()
        c.execute('SELECT value FROM Informations WHERE key = ?', ('globalScoreboardChannelName',))
        result = c.fetchone()
        return result[0] if result else None

    def setGlobalScoreboardChannelName(self, value):
        c = self.conn.cursor()
        c.execute("UPDATE Informations SET value = ? WHERE key='globalScoreboardChannelName';", (value,))
        self.conn.commit()

    def getGlobalNotificationsChannelId(self):
        c = self.conn.cursor()
        c.execute('SELECT value FROM Informations WHERE key = ?', ('globalNotificationsChannelId',))
        result = c.fetchone()
        return result[0] if result else None

    def setGlobalNotificationsChannelId(self, value):
        c = self.conn.cursor()
        c.execute("UPDATE Informations SET value = ? WHERE key='globalNotificationsChannelId';", (value,))
        self.conn.commit()

    def getGlobalNotificationsChannelName(self):
        c = self.conn.cursor()
        c.execute('SELECT value FROM Informations WHERE key = ?', ('globalNotificationsChannelName',))
        result = c.fetchone()
        return result[0] if result else None

    def setGlobalNotificationsChannelName(self, value):
        c = self.conn.cursor()
        c.execute("UPDATE Informations SET value = ? WHERE key='globalNotificationsChannelName';", (value,))
        self.conn.commit()

    def getGlobalScoreboardShouldBeUpdated(self):
        c = self.conn.cursor()
        c.execute('SELECT value FROM Informations WHERE key = ?', ('globalScoreboardShouldBeUpdated',))
        result = c.fetchone()
        return result[0] if result else None

    def setGlobalScoreboardShouldBeUpdated(self, value):
        c = self.conn.cursor()
        c.execute("UPDATE Informations SET value = ? WHERE key='globalScoreboardShouldBeUpdated';", (value,))
        self.conn.commit()
    
    def getLastUpdate(self):
        c = self.conn.cursor()
        c.execute('SELECT value FROM Informations WHERE key = ?', ('lastUpdate',))
        result = c.fetchone()
        return result[0] if result else None

    def setLastUpdate(self, value):
        c = self.conn.cursor()
        c.execute("UPDATE Informations SET value = ? WHERE key='lastUpdate';", (value,))
        self.conn.commit()

