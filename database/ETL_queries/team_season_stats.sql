INSERT INTO Team_Season_Stats (
    team_id,
    season_id,
    mov,
    sos,
    srs,
    o_rtg,
    d_rtg,
    n_rtg,
    pace,
    f_tr,
    x3p_ar,
    ts_percent,
    e_fg_percent,
    tov_percent,
    orb_percent,
    ft_fga,
    opp_e_fg_percent,
    opp_tov_percent,
    opp_drb_percent,
    opp_ft_fga,
    arena,
    attend,
    attend_g
)
SELECT
    t.team_id,
    s.season_id,
    ts.mov,
    ts.sos,
    ts.srs,
    ts.o_rtg,
    ts.d_rtg,
    ts.n_rtg,
    ts.pace,
    ts.f_tr,
    ts.x3p_ar,
    ts.ts_percent,
    ts.e_fg_percent,
    ts.tov_percent,
    ts.orb_percent,
    ts.ft_fga,
    ts.opp_e_fg_percent,
    ts.opp_tov_percent,
    ts.opp_drb_percent,
    ts.opp_ft_fga,
    ts.arena,
    ts.attend,
    ts.attend_g
FROM Team_Summaries AS ts
JOIN Teams AS t 
    ON t.team_name = ts.team  
JOIN Seasons AS s
    ON s.year = ts.season;    


SELECT * FROM Team_Season_Stats;