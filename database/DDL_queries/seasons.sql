CREATE TABLE Seasons (
    season_id INT PRIMARY KEY,
    year DATE,
    season_winner_team_id INT,
    num_players_in_season INT,
    num_teams_in_season INT
);

--INSERT INTO Seasons VALUES (2024, 20, '2024-11-10', 250, 50)

--SELECT * FROM Seasons;

--DELETE FROM Seasons WHERE season_id = 2024;

