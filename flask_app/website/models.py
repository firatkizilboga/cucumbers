from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()
class Player(db.Model):
  __tablename__ = 'players'
  
  Player_ID = db.Column(db.Integer, primary_key=True)
  Player_Name = db.Column(db.String(255), nullable=False)
  Birth_Year = db.Column(db.Integer, nullable=True)
  Num_Seasons = db.Column(db.Integer, nullable=False)
  First_Season = db.Column(db.Integer, nullable=True)
  Last_Season = db.Column(db.Integer, nullable=True)
  MVP_Total = db.Column(db.Integer, default=0)
  HOF = db.Column(db.Boolean, default=False) 
class PlayerSeasonStats(db.Model):
  __tablename__ = 'player_season_stats'

  Season_ID = db.Column(db.Integer, db.ForeignKey('seasons.Season_ID'), primary_key=True)
  Player_ID = db.Column(db.Integer, db.ForeignKey('players.Player_ID'), primary_key=True)
  Games = db.Column(db.Integer, nullable=False)
  PER = db.Column(db.Float, nullable=True)
  TS_Percent = db.Column(db.Float, nullable=True)
  X3p_ar = db.Column(db.Float, nullable=True)
  F_tr = db.Column(db.Float, nullable=True)
  ORB_Percent = db.Column(db.Float, nullable=True)
  DRB_Percent = db.Column(db.Float, nullable=True)
  TRB_Percent = db.Column(db.Float, nullable=True)
  AST_Percent = db.Column(db.Float, nullable=True)
  STL_Percent = db.Column(db.Float, nullable=True)
  BLK_Percent = db.Column(db.Float, nullable=True)
  TOV_Percent = db.Column(db.Float, nullable=True)
  USG_Percent = db.Column(db.Float, nullable=True)
  OWS = db.Column(db.Float, nullable=True)
  DWS = db.Column(db.Float, nullable=True)
  WS = db.Column(db.Float, nullable=True)
  WS_48 = db.Column(db.Float, nullable=True)
  OBPM = db.Column(db.Float, nullable=True)
  DBPM = db.Column(db.Float, nullable=True)
  BPM = db.Column(db.Float, nullable=True)
  VORP = db.Column(db.Float, nullable=True)

  season = db.relationship('Season', backref='player_season_stats', lazy=True)
  player = db.relationship('Player', backref='player_season_stats', lazy=True)
  
  @validates('Games')
  def validate_games(self, games):
    if games < 0:
      raise ValueError("Games can't be less than 0!")
    return games
class PlayerSeasonInfo(db.Model):
  __tablename__ = 'player_season_info'

  Season_ID = db.Column(db.Integer, db.ForeignKey('seasons.Season_ID'), primary_key=True)
  Player_ID = db.Column(db.Integer, db.ForeignKey('players.Player_ID'), primary_key=True)
  Player_Name = db.Column(db.String(255), nullable=False)
  League = db.Column(db.Integer, nullable=True)
  Team_ID = db.Column(db.Integer, db.ForeignKey('teams.Team_ID'), nullable=True)
  Position = db.Column(db.String(20), nullable=True)
  Age = db.Column(db.Integer, nullable=True)
  Experience = db.Column(db.Integer, nullable=True)
  MVP = db.Column(db.Boolean, default=False)
  
  season = db.relationship('Season', backref='player_season_info', lazy=True)
  player = db.relationship('Player', backref='player_season_info', lazy=True)
  team = db.relationship('Team', backref='player_season_info', lazy=True)
  
  @validates('Age')
  def validate_age(self, age):
    if age is not None and age <= 0:
      raise ValueError("Age can't be less than 0!")
    return age
  
  @validates('Experience')
  def validate_experience(self, experience):
    if experience is not None and experience < 0:
      raise ValueError("Experience can't be less than 0!")
    return experience