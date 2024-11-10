CREATE TABLE PLAYERS_SEASON (
    Player_ID INT,
    Player_Name VARCHAR(255) NOT NULL,
    Season_ID INT,
    Team_ID INT,
    Position VARCHAR(20),
    Age INT CHECK (Age > 0),
    Experience INT CHECK (Experience >= 0),
    MVP BOOLEAN DEFAULT FALSE,

    PRIMARY KEY (Player_ID, Season_ID),
    FOREIGN KEY (Season_ID) REFERENCES SEASONS(Season_ID),
    FOREIGN KEY (Team_ID) REFERENCES TEAMS(Team_ID)
);