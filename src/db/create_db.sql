CREATE TABLE Users (
    usernameID TEXT, -- Unique username
    usernameDN TEXT, -- Display username
    points INTEGER,
    allChallengesRetrieved INTEGER, -- If 1 then all flagged challenges have been retrieved throught the API, 0 otherwise
    PRIMARY KEY (usernameID)
);

CREATE TABLE Autored (
    username TEXT,
    title TEXT,
    PRIMARY KEY (username, title),
    FOREIGN KEY (username) REFERENCES Users(usernameID)
);

CREATE TABLE Flagged (
    username TEXT,
    title TEXT,
    PRIMARY KEY (username, title),
    FOREIGN KEY (username) REFERENCES Users(usernameID)
);
