INSERT INTO Team_Season_Info (
    team_id,
    season_id,
    league,
    abbreviation,
    playoffs,
    age,
    w,
    l,
    pw,
    pl
)
SELECT
    t.team_id,
    s.season_id,
    ts.lg AS league,
    ts.abbreviation,
    ts.playoffs,
    ts.age,
    ts.w,
    ts.l,
    ts.pw,
    ts.pl
FROM Team_Summaries AS ts
JOIN Teams AS t
    ON t.team_name = ts.team
JOIN Seasons AS s
    ON s.year = ts.season;

    SELECT * FROM Team_Season_Info;
