DROP TABLE IF EXISTS Team_Season_Stats;

CREATE TABLE Team_Season_Stats (
    team_id INT,
    season_id INT,
    mov FLOAT,
    sos FLOAT,
    srs FLOAT,
    o_rtg FLOAT,
    d_rtg FLOAT,
    n_rtg FLOAT,
    pace FLOAT,
    f_tr FLOAT,
    x3p_ar FLOAT,
    ts_percent FLOAT,
    e_fg_percent FLOAT,
    tov_percent FLOAT,
    orb_percent FLOAT,
    ft_fga FLOAT,
    opp_e_fg_percent FLOAT,
    opp_tov_percent FLOAT,
    opp_drb_percent FLOAT,
    opp_ft_fga FLOAT,
    arena VARCHAR(255),
    attend INT,
    attend_g INT,
    PRIMARY KEY (team_id, season_id),
    FOREIGN KEY (season_id) REFERENCES seasons(season_id) ON DELETE CASCADE
);