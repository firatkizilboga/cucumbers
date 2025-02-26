DROP TABLE IF EXISTS Players;

CREATE TABLE Players (
    Player_ID INT,
    Player VARCHAR(255) NOT NULL,
    Birth_Year INT, -- some values in dataset are NULL
    Num_Seasons INT CHECK (Num_Seasons > 0),
    First_Seas INT,
    Last_Seas INT,
    MVP_Total INT DEFAULT 0,
    HOF BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (Player_ID)
);

-- INSERT INTO Players
-- values (1, 'LeBron James', 2002, 25, 2010, 2025, 5, FALSE);
-- SELECT * FROM Players;
-- DELETE FROM Players WHERE Player_ID = 1;
