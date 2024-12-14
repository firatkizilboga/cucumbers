import os
import pandas as pd
from sqlalchemy import create_engine

# Database connection details
MYSQL_USER = "admin"
MYSQL_PASSWORD = "31cuCUMbers"
MYSQL_HOST = "134.122.79.205"
MYSQL_PORT = 3306
MYSQL_DATABASE = "cucumdb"

# Directory containing the files
NBA_SHOTS_DIR = "NBA-Shots"

# Create SQLAlchemy engine
engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

# Define column mapping to match the database schema
COLUMN_MAPPING = {
    "SEASON_1": "Season_ID",
    "SEASON_2": None,  # Ignored
    "TEAM_ID": "Team_ID",
    "TEAM_NAME": None,  # Ignored
    "PLAYER_ID": "Player_ID",
    "PLAYER_NAME": None,  # Ignored
    "POSITION_GROUP": "Position_Group",
    "POSITION": "Position",
    "GAME_DATE": "Game_Date",
    "GAME_ID": "Game_ID",
    "HOME_TEAM": "Home_Team",
    "AWAY_TEAM": "Away_Team",
    "EVENT_TYPE": "Event_Type",
    "SHOT_MADE": "Shot_Made",
    "ACTION_TYPE": "Action_Type",
    "SHOT_TYPE": "Shot_Type",
    "BASIC_ZONE": "Basic_Zone",
    "ZONE_NAME": "Zone_Name",
    "ZONE_ABB": "Zone_Abb",
    "ZONE_RANGE": "Zone_Range",
    "LOC_X": "Loc_X",
    "LOC_Y": "Loc_Y",
    "SHOT_DISTANCE": "Shot_Distance",
    "QUARTER": "Quarter",
    "MINS_LEFT": "Mins_Left",
    "SECS_LEFT": "Secs_Left",
}

# Filter out columns set to None in the mapping
valid_columns = {old: new for old, new in COLUMN_MAPPING.items() if new}

# Process all files in the directory
for filename in os.listdir(NBA_SHOTS_DIR):
    if filename.endswith(".csv"):
        file_path = os.path.join(NBA_SHOTS_DIR, filename)

        # Read the CSV file
        data = pd.read_csv(file_path)

        # Map columns to match the database schema
        data = data.rename(columns=valid_columns)

        # Select only the valid columns
        data = data[list(valid_columns.values())]

        # Insert data into the database
        data.to_sql("game_shots", engine, if_exists="append", index=False)
        print(f"Inserted {len(data)} rows from {filename} into Game_Shots.")

print("All data has been inserted successfully.")
