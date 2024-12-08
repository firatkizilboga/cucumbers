DROP TABLE IF EXISTS Player_Season_Info;

CREATE TABLE Player_Season_Info (
    Season_ID INT,
    Player_ID INT,
    Player_Name VARCHAR(255) NOT NULL,
    League INT,
    Team_ID INT,
    Position VARCHAR(20),
    Age INT CHECK (Age > 0),
    Experience INT CHECK (Experience >= 0),
    MVP BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (Season_ID, Player_ID),
    FOREIGN KEY (Season_ID) REFERENCES Seasons (Season_ID),
    FOREIGN KEY (Player_ID) REFERENCES Players (Player_ID),
    FOREIGN KEY (Team_ID) REFERENCES Teams (Team_ID)
);
