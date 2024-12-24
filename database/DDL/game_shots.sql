DROP TABLE IF EXISTS Game_Shots;


CREATE TABLE Game_Shots (
    Game_ID INT,
    Season_ID INT,
    Team_ID INT,
    Player_ID INT,
    Position_Group VARCHAR(50), -- Categorical grouping
    Position VARCHAR(20),       -- Specific position (e.g., "PG", "SG")
    Game_Date DATE,
    Home_Team VARCHAR(50),
    Away_Team VARCHAR(50),
    Event_Type VARCHAR(50),     -- Event type (e.g., "Shot", "Rebound")
    Shot_Made BOOLEAN,          -- True for made, False for missed
    Action_Type VARCHAR(100),   -- Specific action type of the shot
    Shot_Type VARCHAR(50),      -- E.g., "2PT Field Goal", "3PT Field Goal"
    Basic_Zone VARCHAR(50),     -- General area on the court (e.g., "Paint", "Mid-Range")
    Zone_Name VARCHAR(50),      -- Specific zone name
    Zone_Abb VARCHAR(20),       -- Abbreviation for the zone (e.g., "RA" for Restricted Area)
    Zone_Range VARCHAR(50),     -- Range description (e.g., "0-8 ft", "24+ ft")
    Loc_X DECIMAL(5, 2),         -- X-coordinate of the shot
    Loc_Y DECIMAL(5, 2),         -- Y-coordinate of the shot
    Shot_Distance DECIMAL(5, 2), -- Distance of the shot in feet
    Quarter INT CHECK (Quarter BETWEEN 1 AND 4), -- Quarter of the game
    Mins_Left INT CHECK (Mins_Left BETWEEN 0 AND 11), -- Minutes left in the quarter
    Secs_Left INT CHECK (Secs_Left BETWEEN 0 AND 59), -- Seconds left in the minute
    -- Foreign Key Constraints
    FOREIGN KEY (Season_ID) REFERENCES Seasons (Season_ID),
    FOREIGN KEY (Player_ID) REFERENCES Players (Player_ID),
    FOREIGN KEY (Team_ID) REFERENCES Teams (Team_ID)
)
ENGINE=InnoDB;

-- 2. Add Partitioning by Year (assuming Game_Date determines the year)
ALTER TABLE Game_Shots
PARTITION BY RANGE (YEAR(Game_Date)) (
    PARTITION p2004 VALUES LESS THAN (2005),
    PARTITION p2005 VALUES LESS THAN (2006),
    PARTITION p2006 VALUES LESS THAN (2007),
    PARTITION p2007 VALUES LESS THAN (2008),
    PARTITION p2008 VALUES LESS THAN (2009),
    PARTITION p2009 VALUES LESS THAN (2010),
    PARTITION p2010 VALUES LESS THAN (2011),
    PARTITION p2011 VALUES LESS THAN (2012),
    PARTITION p2012 VALUES LESS THAN (2013),
    PARTITION p2013 VALUES LESS THAN (2014),
    PARTITION p2014 VALUES LESS THAN (2015),
    PARTITION p2015 VALUES LESS THAN (2016),
    PARTITION p2016 VALUES LESS THAN (2017),
    PARTITION p2017 VALUES LESS THAN (2018),
    PARTITION p2018 VALUES LESS THAN (2019),
    PARTITION p2019 VALUES LESS THAN (2020),
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION pMax VALUES LESS THAN MAXVALUE
);

-- 3. Create an index on Player_ID for faster lookups
CREATE INDEX idx_player_id ON Game_Shots (Player_ID);

--4. Generate Primary Key
ALTER TABLE `Game_Shots` ADD COLUMN `shot_id` BIGINT UNSIGNED NULL AFTER `Season_ID`;

WITH ShotNumbers AS (
         SELECT
             Game_ID,
             Season_ID,
             ROW_NUMBER() OVER (
                 PARTITION BY Season_ID
                 ORDER BY Game_Date, Game_ID, Player_ID
             ) AS rn
         FROM
             `Game_Shots`
     )
     UPDATE `Game_Shots` g
     JOIN ShotNumbers s
         ON g.Game_ID = s.Game_ID AND g.Season_ID = s.Season_ID
     SET g.shot_id = s.rn;

ALTER TABLE `Game_Shots`
    MODIFY COLUMN `shot_id` INT NOT NULL;

-- 5. Create Primary Key Constraint 
ALTER TABLE `Game_Shots`
    ADD PRIMARY KEY (`Season_ID`, `shot_id`);
