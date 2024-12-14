import os
import pandas as pd
from sqlalchemy import create_engine

# Database connection details
MYSQL_USER = "cucumber"
MYSQL_PASSWORD = "1234"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "cucumdb"

engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

COLUMN_MAPPING = {
  'season': 'Season',
  'award': 'Award',
  'player': 'Player',
  'age': 'Age',
  'tm': 'Team',
  'first': 'First',
  'pts_won': 'Points_Won',
  'pts_max': 'Points_Max',
  'share': 'Share',
  'winner': 'Winner',
  'seas_id': 'Season_ID',
  'player_id': 'Player_ID'
}

raw_data_dir = os.path.join(os.path.dirname(__file__), '..', 'raw_data', 'nba')
csv_path = os.path.join(raw_data_dir, 'Player_Award_Shares.csv')

if not os.path.exists(csv_path):
  raise FileNotFoundError(f"CSV file not found: {csv_path}")

df = pd.read_csv(csv_path)
df = df.rename(columns=COLUMN_MAPPING)

df.to_sql('player_award_shares', con=engine, if_exists='replace', index=False)
    
print("Data populated successfully!")