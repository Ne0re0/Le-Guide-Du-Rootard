CREATE TABLE Users (
    usernameID TEXT, -- Unique username
    usernameDN TEXT, -- Display username
    points INTEGER,
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
