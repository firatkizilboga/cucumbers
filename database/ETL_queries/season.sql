INSERT INTO Seasons (year, season_winner_team_id, num_players_in_season, num_teams_in_season)
WITH STEP1 AS (
    SELECT season as season_year,
        count(distinct player) as num_players_in_season,
        count(distinct tm) as num_teams_in_season
    FROM Player_Season_Info
    GROUP BY 1
)
select season_year,
    Teams.team_id,
    num_players_in_season,
    num_teams_in_season
FROM STEP1
    LEFT JOIN Finals on season_year = Finals.Year
    LEFT JOIN Teams on Teams.team_name = Finals.`NBA Champion`
    where team_abbreviation is not null


SELECT * FROM Seasons