DROP TABLE IF EXISTS Player_Season_Stats;

CREATE TABLE Player_Season_Stats (
    Season_ID INT,
    Player_ID INT,
    Games INT CHECK (Games >= 0),
    PER FLOAT,
    TS_Percent FLOAT,
    X3p_ar FLOAT,
    F_tr FLOAT,
    ORB_Percent FLOAT,
    DRB_Percent FLOAT,
    TRB_Percent FLOAT,
    AST_Percent FLOAT,
    STL_Percent FLOAT,
    BLK_Percent FLOAT,
    TOV_Percent FLOAT,
    USG_Percent FLOAT,
    OWS FLOAT,
    DWS FLOAT,
    WS FLOAT,
    WS_48 FLOAT,
    OBPM FLOAT,
    DBPM FLOAT,
    BPM FLOAT,
    VORP FLOAT,
    PRIMARY KEY (Season_ID, Player_ID),
    FOREIGN KEY (Season_ID) REFERENCES Seasons (Season_ID) ON DELETE CASCADE,
    FOREIGN KEY (Player_ID) REFERENCES Players (Player_ID) ON DELETE CASCADE
);

CREATE INDEX i_season ON Player_Season_Stats (Season_ID);
CREATE INDEX i_player ON Player_Season_Stats (Player_ID);