-- Start a transaction to ensure atomicity
START TRANSACTION;

-- Insert data into Game_Shots from Game_Shots_Raw with necessary joins and transformations
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
SELECT
    gsr.Game_ID,
    s.Season_ID,
    pis.Team_ID,
    pis.Player_ID,
    gsr.POSITION_GROUP,
    gsr.POSITION,
    STR_TO_DATE(gsr.GAME_DATE, '%m-%d-%Y') AS Game_Date, -- Adjust format if necessary
    gsr.HOME_TEAM,
    gsr.AWAY_TEAM,
    gsr.EVENT_TYPE,
    IF(gsr.SHOT_MADE = 1, TRUE, FALSE) AS Shot_Made, -- Corrected handling of Shot_Made
    gsr.ACTION_TYPE,
    gsr.SHOT_TYPE,
    gsr.BASIC_ZONE,
    gsr.ZONE_NAME,
    gsr.ZONE_ABB,
    gsr.ZONE_RANGE,
    CAST(gsr.LOC_X AS DECIMAL(5,2)) AS Loc_X,
    CAST(gsr.LOC_Y AS DECIMAL(5,2)) AS Loc_Y,
    CAST(gsr.SHOT_DISTANCE AS DECIMAL(5,2)) AS Shot_Distance,
    CAST(gsr.QUARTER AS UNSIGNED) AS Quarter,
    CAST(gsr.MINS_LEFT AS UNSIGNED) AS Mins_Left,
    CAST(gsr.SECS_LEFT AS UNSIGNED) AS Secs_Left
FROM
    Game_Shots_Raw gsr
INNER JOIN Seasons s 
    ON s.year = gsr.SEASON_1
INNER JOIN Player_Info_Per_Season pis 
    ON pis.Season_ID = s.Season_ID 
    AND pis.Player_Name = gsr.PLAYER_NAME;

-- Commit the transaction after successful insertion
COMMIT;
