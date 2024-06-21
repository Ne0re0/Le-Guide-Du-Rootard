CREATE TABLE Autored (
    username TEXT,
    title TEXT,
    PRIMARY KEY (username, title)
);

CREATE TABLE Users (
    username TEXT,
    PRIMARY KEY (username)
);

CREATE TABLE Flagged (
    username TEXT,
    title TEXT,
    PRIMARY KEY (username, title)
);
