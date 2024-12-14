CREATE TABLE advanced (
    Season_ID INT,
    Season INT,
    Player_ID INT,
    Player VARCHAR(100),
    Birth_Year INT,
    Pos VARCHAR(5),
    Age INT,
    Experience INT,
    LG VARCHAR(5),
    Team VARCHAR(10),
    G INT,
    MP INT,
    PER DECIMAL(5,2),
    TS_Percent DECIMAL(5,3),
    X3P_AR DECIMAL(5,3),
    F_TR DECIMAL(5,3),
    ORB_Percent DECIMAL(5,3),
    DRB_Percent DECIMAL(5,3),
    TRB_Percent DECIMAL(5,3),
    AST_Percent DECIMAL(5,3),
    STL_Percent DECIMAL(5,3),
    BLK_Percent DECIMAL(5,3),
    TOV_Percent DECIMAL(5,3),
    USG_Percent DECIMAL(5,3),
    OWS DECIMAL(5,2),
    DWS DECIMAL(5,2),
    WS DECIMAL(5,2),
    WS_48 DECIMAL(5,3),
    OBPM DECIMAL(5,3),
    DBPM DECIMAL(5,3),
    BPM DECIMAL(5,3),
    VORP DECIMAL(5,3)
);

CREATE TABLE player_award_shares(
    Season INT,                   -- Year of the award season
    Award VARCHAR(50),            -- Name of the award
    Player VARCHAR(100),          -- Player's full name
    Age INT,                      -- Age of the player
    Team VARCHAR(10),             -- Team abbreviation (e.g., GSW, CHI)
    First INT,                    -- Number of first-place votes
    Points_Won INT,               -- Total points won by the player
    Points_Max INT,               -- Maximum possible points
    Share DECIMAL(5, 3),          -- Share of points won (ratio, e.g., 0.602)
    Winner BOOLEAN,               -- TRUE if the player won the award, FALSE otherwise
    Season_ID INT,                -- Unique identifier for the season
    Player_ID INT,                -- Unique identifier for the player
);

CREATE TABLE team_summaries(
    Season INT,                      -- Season year
    League VARCHAR(10),              -- League name (e.g., NBA)
    Team_Name VARCHAR(50),           -- Full name of the team
    Abbreviation VARCHAR(10),        -- Abbreviation for the team
    Playoffs BOOLEAN,                -- Whether the team made the playoffs (TRUE/FALSE)
    Age DECIMAL(4, 1),               -- Average team age
    Wins INT,                        -- Number of wins
    Losses INT,                      -- Number of losses
    Pythagorean_Wins INT,            -- Pythagorean expectation wins
    Pythagorean_Losses INT,          -- Pythagorean expectation losses
    MOV DECIMAL(5, 2),               -- Margin of victory
    SOS DECIMAL(5, 2),               -- Strength of schedule
    SRS DECIMAL(5, 2),               -- Simple rating system (MOV adjusted for SOS)
    Offensive_Rating DECIMAL(5, 1),  -- Offensive rating (points per 100 possessions)
    Defensive_Rating DECIMAL(5, 1),  -- Defensive rating (points allowed per 100 possessions)
    Net_Rating DECIMAL(5, 1),        -- Net rating (Offensive - Defensive rating)
    Pace DECIMAL(5, 1),              -- Pace factor (possessions per 48 minutes)
    Free_Throw_Rate DECIMAL(5, 3),   -- Free throw rate (FTA/FGA)
    Three_Point_Attempt_Rate DECIMAL(5, 3), -- 3-point attempt rate (3PA/FGA)
    TS_Percentage DECIMAL(5, 3),     -- True shooting percentage
    EFG_Percentage DECIMAL(5, 3),    -- Effective field goal percentage
    Turnover_Percentage DECIMAL(5, 1), -- Turnover percentage
    Offensive_Rebound_Percentage DECIMAL(5, 1), -- Offensive rebound percentage
    Free_Throws_Per_FGA DECIMAL(5, 3), -- Free throws made per field goal attempt
    Opponent_EFG_Percentage DECIMAL(5, 3), -- Opponent effective field goal percentage
    Opponent_Turnover_Percentage DECIMAL(5, 1), -- Opponent turnover percentage
    Opponent_Defensive_Rebound_Percentage DECIMAL(5, 1), -- Opponent defensive rebound percentage
    Opponent_FT_Per_FGA DECIMAL(5, 3), -- Opponent free throws per field goal attempt
    Arena VARCHAR(100),              -- Name of the team's arena
    Attendance INT,                  -- Total season attendance
    Attendance_Per_Game INT        -- Average attendance per game
);

CREATE TABLE game_shots (
    Game_ID INT,
    Season_ID INT,
    Team_ID INT,
    Player_ID INT,
    Position_Group VARCHAR(50), -- Assuming this is a categorical grouping
    Position VARCHAR(20), -- Assuming this is a specific position (e.g., "PG", "SG")
    Game_Date DATE,
    Home_Team VARCHAR(50),
    Away_Team VARCHAR(50),
    Event_Type VARCHAR(50), -- For event type (e.g., "Shot", "Rebound")
    Shot_Made BOOLEAN, -- True for made, False for missed
    Action_Type VARCHAR(100), -- Specific action type of the shot
    Shot_Type VARCHAR(50), -- E.g., "2PT Field Goal", "3PT Field Goal"
    Basic_Zone VARCHAR(50), -- General area on the court (e.g., "Paint", "Mid-Range")
    Zone_Name VARCHAR(50), -- Specific zone name
    Zone_Abb VARCHAR(20), -- Abbreviation for the zone (e.g., "RA" for Restricted Area)
    Zone_Range VARCHAR(50), -- Range description (e.g., "0-8 ft", "24+ ft")
    Loc_X DECIMAL(5, 2), -- X-coordinate of the shot
    Loc_Y DECIMAL(5, 2), -- Y-coordinate of the shot
    Shot_Distance DECIMAL(5, 2), -- Distance of the shot in feet
    Quarter INT CHECK (Quarter BETWEEN 1 AND 4), -- Quarter of the game
    Mins_Left INT CHECK (Mins_Left BETWEEN 0 AND 11), -- Minutes left in the quarter
    Secs_Left INT CHECK (Secs_Left BETWEEN 0 AND 59) -- Seconds left in the minute
);

