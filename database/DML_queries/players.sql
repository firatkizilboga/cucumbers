CREATE TABLE PLAYERS (
    Player_ID INT,
    Player_Name VARCHAR(255) NOT NULL,
    HOF BOOLEAN DEFAULT FALSE,
    Birth_Year INT, -- some values in dataset are NULL
    Num_Seasons INT CHECK (Num_Seasons > 0),
    First_Season INT,
    Last_Season INT CHECK (Last_Season >= First_Season),
    MVP_Total INT DEFAULT 0,
    Diff_Teams INT CHECK (Diff_Teams > 0),
    Num_Dunks INT CHECK (Num_Dunks >= 0),

    PRIMARY KEY (Player_ID)
);