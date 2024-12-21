DROP TABLE IF EXISTS Team_Season_Info;

CREATE TABLE Team_Season_Info (
    team_id INT,
    season_id INT,
    league VARCHAR(50),
    abbreviation VARCHAR(10),
    playoffs BOOLEAN,
    age DECIMAL(3,1),
    w INT,
    l INT,
    pw INT,
    pl INT,

    PRIMARY KEY(team_id, season_id),
    FOREIGN KEY (season_id) REFERENCES Seasons(season_id) ON DELETE CASCADE
);