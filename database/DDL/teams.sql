DROP TABLE IF EXISTS Teams;

CREATE TABLE Teams (
    team_id INT AUTO_INCREMENT,
    team_name VARCHAR(255) NOT NULL,
    team_abbreviation VARCHAR(255) NOT NULL,
    PRIMARY KEY (team_id)
);
