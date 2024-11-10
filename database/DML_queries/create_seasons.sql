CREATE TABLE SeasonFact (
    season_id INT PRIMARY KEY,
    season_winner_team_id INT,
    season_date DATE,
    num_players_in_season INT,
    num_teams_in_season INT
);

--INSERT INTO SeasonFact VALUES (2024, 20, '2024-11-10', 250, 50)

--SELECT * FROM SeasonFact;

--DELETE FROM SeasonFact WHERE season_id = 2024;