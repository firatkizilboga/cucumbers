-- SELECT * FROM Player_Career_Info;

-- SELECT 
--     pas.Player_ID, 
--     COUNT(*) AS MVP_Total
--   FROM Player_Award_Shares pas
--   WHERE pas.Award = 'nba mvp' AND pas.Winner = TRUE
--   GROUP BY pas.Player_ID
INSERT INTO Players (
  Player_ID, Player, Birth_Year, Num_Seasons, First_Seas, Last_Seas, MVP_Total, HOF
  )
SELECT 
  pci.Player_ID,
  pci.player,
  pci.Birth_Year,
  pci.Num_Seasons,
  pci.First_Seas,
  pci.Last_Seas,
  mvp_counts.MVP_Total,  -- This will be NULL if no MVPs for the player
  pci.HOF
FROM Player_Career_Info pci
LEFT JOIN (
  SELECT 
    pas.Player_ID, 
    COUNT(*) AS MVP_Total
  FROM Player_Award_Shares pas
  WHERE pas.Award = 'nba mvp' AND pas.Winner = TRUE
  GROUP BY pas.Player_ID
) AS mvp_counts
ON pci.Player_ID = mvp_counts.Player_ID;

-- SELECT * FROM Players;

INSERT INTO Player_Season_Stats (
  Season_ID, Player_ID, Games, PER, TS_Percent, X3p_ar, F_tr, ORB_Percent, DRB_Percent, TRB_Percent,
  AST_Percent, STL_Percent, BLK_Percent, TOV_Percent, USG_Percent, OWS, DWS, WS, WS_48, OBPM, DBPM, BPM, VORP
)
SELECT
  s.season_id,
  p.player_id,
  a.g,
  a.per,
  a.ts_percent,
  a.x3p_ar,
  a.f_tr,
  a.orb_percent,
  a.drb_percent,
  a.trb_percent,
  a.ast_percent,
  a.stl_percent,
  a.blk_percent,
  a.tov_percent,
  a.usg_percent,
  a.ows,
  a.dws,
  a.ws,
  a.ws_48,
  a.obpm,
  a.dbpm,
  a.bpm,
  a.vorp
FROM Advanced a
JOIN Seasons s ON a.season = s.year
JOIN Players p ON a.player_id = p.player_id
WHERE g = (
	SELECT max(g) FROM Advanced a1 WHERE a1.player_id = a.player_id and a1.season = s.year
);

SELECT * FROM Player_Season_Stats;

-- INSERT INTO Player_Info_Per_Season (
--   Season_ID, Player_ID, Player_Name, League, Team_ID, Position, Age, Experience, MVP
-- )
-- SELECT
--   s.season_id,
--   p.Player_ID,
--   p.Player,
--   adv.lg AS League,
--   t.team_id,
--   adv.pos AS Position,
--   adv.age AS Age,
--   adv.experience AS Experience,
--   CASE 
--     WHEN pas.winner = TRUE AND pas.award = 'nba mvp' THEN TRUE 
--     ELSE FALSE 
--   END AS MVP
-- FROM Advanced AS adv
-- JOIN Players AS p
--   ON p.Player_ID = adv.player_id
-- JOIN Seasons AS s
--   ON s.year = adv.season
-- JOIN Teams AS t
--   ON adv.tm LIKE CONCAT('%', t.team_abbreviation, '%')
-- LEFT JOIN Player_Award_Shares pas
--   ON adv.player_id = pas.Player_ID 
--   AND adv.season = pas.season
-- WHERE g = (
-- 	SELECT max(g) FROM Advanced a1 WHERE a1.player_id = adv.player_id and a1.season = s.year
-- );

INSERT INTO Player_Info_Per_Season (
  Season_ID, 
  Player_ID, 
  Player_Name, 
  League, 
  Team_ID, 
  Position, 
  Age, 
  Experience, 
  MVP
)
SELECT
  s.season_id,
  p.Player_ID,
  p.Player,
  adv.lg AS League,
  t.team_id,
  adv.pos AS Position,
  adv.age AS Age,
  adv.experience AS Experience,
  CASE
    WHEN adv.is_mvp = 1 THEN TRUE
    ELSE FALSE
  END AS MVP
FROM (
  SELECT 
    adv.*,
    CASE
      WHEN pas.winner = TRUE AND pas.award = 'nba mvp' THEN 1
      ELSE 0
    END AS is_mvp,
    ROW_NUMBER() OVER (
      PARTITION BY adv.player_id, adv.season 
      ORDER BY adv.g DESC, 
        CASE WHEN pas.winner = TRUE AND pas.award = 'nba mvp' THEN 1 ELSE 0 END DESC
    ) AS rn
  FROM Advanced AS adv
  LEFT JOIN Player_Award_Shares pas
    ON adv.player_id = pas.Player_ID
    AND adv.season = pas.season
) AS adv
JOIN Players AS p 
  ON p.Player_ID = adv.player_id
JOIN Seasons AS s 
  ON s.year = adv.season
LEFT JOIN Teams AS t 
  ON adv.tm = t.team_abbreviation -- Optimized JOIN condition
WHERE adv.rn = 1;

-- SELECT DISTINCT Position
-- FROM Player_Info_Per_Season;
