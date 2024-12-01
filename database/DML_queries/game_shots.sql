CREATE TABLE Game_Shots (
  Game_ID INT,
  Season_ID INT,
  Team_ID INT,
  Player_ID INT,
  Position_Group VARCHAR(50), -- Assuming this is a categorical grouping
  Position VARCHAR(20),       -- Assuming this is a specific position (e.g., "PG", "SG")
  Game_Date DATE,
  Home_Team VARCHAR(50),
  Away_Team VARCHAR(50),
  Event_Type VARCHAR(50),     -- For event type (e.g., "Shot", "Rebound")
  Shot_Made BOOLEAN,          -- True for made, False for missed
  Action_Type VARCHAR(100),   -- Specific action type of the shot
  Shot_Type VARCHAR(50),      -- E.g., "2PT Field Goal", "3PT Field Goal"
  Basic_Zone VARCHAR(50),     -- General area on the court (e.g., "Paint", "Mid-Range")
  Zone_Name VARCHAR(50),      -- Specific zone name
  Zone_Abb VARCHAR(20),       -- Abbreviation for the zone (e.g., "RA" for Restricted Area)
  Zone_Range VARCHAR(50),     -- Range description (e.g., "0-8 ft", "24+ ft")
  Loc_X DECIMAL(5,2),                  -- X-coordinate of the shot
  Loc_Y DECIMAL(5,2),                  -- Y-coordinate of the shot
  Shot_Distance DECIMAL(5,2),        -- Distance of the shot in feet
  Quarter INT CHECK (Quarter BETWEEN 1 AND 4), -- Quarter of the game
  Mins_Left INT CHECK (Mins_Left BETWEEN 0 AND 11), -- Minutes left in the quarter
  Secs_Left INT CHECK (Secs_Left BETWEEN 0 AND 59), -- Seconds left in the minute

  PRIMARY KEY (Game_ID, Player_ID, LOC_X, LOC_Y),
  FOREIGN KEY (Season_ID) REFERENCES Seasons(Season_ID),
  FOREIGN KEY (Player_ID) REFERENCES Players(Player_ID),
  FOREIGN KEY (Team_ID) REFERENCES Teams(Team_ID)
);

INSERT INTO Game_Shots (
  Game_ID,
  Season_ID,
  Team_ID,
  Player_ID,
  Position_Group,
  Position,
  Game_Date,
  Home_Team,
  Away_Team,
  Event_Type,
  Shot_Made,
  Action_Type,
  Shot_Type,
  Basic_Zone,
  Zone_Name,
  Zone_Abb,
  Zone_Range,
  Loc_X,
  Loc_Y,
  Shot_Distance,
  Quarter,
  Mins_Left,
  Secs_Left
)
VALUES (
  1001,               -- Game_ID
  2024,               -- Season_ID
  101,                -- Team_ID
  23,                 -- Player_ID
  'Forward',          -- Position_Group
  'SF',               -- Position
  '2024-11-30',       -- Game_Date
  'Los Angeles Lakers', -- Home_Team
  'Boston Celtics',   -- Away_Team
  'Shot',             -- Event_Type
  TRUE,               -- Shot_Made
  'Jump Shot',        -- Action_Type
  '2PT Field Goal',   -- Shot_Type
  'Paint',            -- Basic_Zone
  'Restricted Area',  -- Zone_Name
  'RA',               -- Zone_Abb
  '0-8 ft',           -- Zone_Range
  5.25,               -- Loc_X
  -1.75,              -- Loc_Y
  7.5,                -- Shot_Distance
  2,                  -- Quarter
  3,                  -- Mins_Left
  45                  -- Secs_Left
);

