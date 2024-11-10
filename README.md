# cucumbers

init the db with:
docker compose -f compose.yaml up -d

run the mysql container in tty:
docker exec -it mysql bash

run mysql server as root account:
mysql -u root -p

# DB Schemas

Seasons (**season_id**, year)

Teams (**team_id**, team_name)

Players (**player_id**, name, birth_year)

Game_Shots (**game_id**, **season_id**,**team_id**,**player_id**,POSITION_GROUP,POSITION,GAME_DATE,HOME_TEAM,AWAY_TEAM,EVENT_TYPE,SHOT_MADE,ACTION_TYPE,SHOT_TYPE,BASIC_ZONE,ZONE_NAME,ZONE_ABB,ZONE_RANGE,LOC_X,LOC_Y,SHOT_DISTANCE,QUARTER,MINS_LEFT,SECS_LEFT ) 

Team_Season_Info(**team_id**,**season_id**,league,abbreviation,playoffs,age,w,l,pw,pl)

Team_Season_Stats(**team_id**,**season_id**,mov,sos,srs,o_rtg,d_rtg,n_rtg,pace,f_tr,x3p_ar,ts_percent,e_fg_percent,tov_percent,orb_percent,ft_fga,opp_e_fg_percent,opp_tov_percent,opp_drb_percent,opp_ft_fga,arena,attend,attend_g) 

Player_Season_Info(**season_id**,**player_id**,pos,age,experience,lg,tm) 

Player_Season_Stats(**season_id**,**player_id**,g,mp,per,ts_percent,x3p_ar,f_tr,orb_percent,drb_percent,trb_percent,ast_percent,stl_percent,blk_percent,tov_percent,usg_percent,ows,dws,ws,ws_48,obpm,dbpm,bpm,vorp)
