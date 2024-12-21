DROP TABLE IF EXISTS Player_Info_Per_Season;

CREATE TABLE Player_Info_Per_Season (
    Season_ID INT,
    Player_ID INT,
    Player_Name VARCHAR(255) NOT NULL,
    League VARCHAR(50),
    Team_ID INT,
    Position VARCHAR(20),
    Age INT CHECK (Age > 0),
    Experience INT CHECK (Experience >= 0),
    MVP BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (Season_ID, Player_ID),
    FOREIGN KEY (Season_ID) REFERENCES Seasons (Season_ID) ON DELETE CASCADE,
    FOREIGN KEY (Player_ID) REFERENCES Players (Player_ID) ON DELETE CASCADE,
    FOREIGN KEY (Team_ID) REFERENCES Teams (Team_ID) ON DELETE SET NULL
);
