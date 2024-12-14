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

SELECT * FROM Players