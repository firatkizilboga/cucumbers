INSERT INTO Teams (team_name, team_abbreviation)
SELECT 
    team AS team_name,
    GROUP_CONCAT(DISTINCT abbreviation ORDER BY abbreviation ASC SEPARATOR ', ') AS team_abbreviation
FROM Team_Abbrev
WHERE abbreviation IS NOT NULL AND team IS NOT NULL
GROUP BY team;


SELECT * FROM Teams;