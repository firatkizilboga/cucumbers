INSERT INTO Teams (team_name, team_abbreviation) 
SELECT DISTINCT
    team,
    abbreviation
FROM Team_Abbrev
WHERE 1=1
    AND abbreviation IS NOT NULL
    AND team IS NOT NULL
    ;

SELECT * FROM Teams;