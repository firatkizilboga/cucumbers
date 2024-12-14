import os
import pandas as pd
from sqlalchemy import create_engine

# Database connection details
MYSQL_USER = "cucumber"
MYSQL_PASSWORD = "1234"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "cucumdb"

# Create SQLAlchemy engine
engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

# Define column mapping to match the database schema
COLUMN_MAPPING = {
    "season": "Season",  # Maps season to Season
    "lg": "League",  # Maps lg to League
    "team": "Team_Name",  # Maps team to Team_Name
    "abbreviation": "Abbreviation",  # Maps abbreviation to Abbreviation
    "playoffs": "Playoffs",  # Maps playoffs to Playoffs
    "age": "Age",  # Maps age to Age
    "w": "Wins",  # Maps w to Wins
    "l": "Losses",  # Maps l to Losses
    "pw": "Pythagorean_Wins",  # Maps pw to Pythagorean_Wins
    "pl": "Pythagorean_Losses",  # Maps pl to Pythagorean_Losses
    "mov": "Margin_Of_Victory",  # Maps mov to Margin_Of_Victory
    "sos": "Strength_Of_Schedule",  # Maps sos to Strength_Of_Schedule
    "srs": "Simple_Rating_System",  # Maps srs to Simple_Rating_System
    "o_rtg": "Offensive_Rating",  # Maps o_rtg to Offensive_Rating
    "d_rtg": "Defensive_Rating",  # Maps d_rtg to Defensive_Rating
    "n_rtg": "Net_Rating",  # Maps n_rtg to Net_Rating
    "pace": "Pace",  # Maps pace to Pace
    "f_tr": "Free_Throw_Rate",  # Maps f_tr to Free_Throw_Rate
    "x3p_ar": "Three_Point_Attempt_Rate",  # Maps x3p_ar to Three_Point_Attempt_Rate
    "ts_percent": "True_Shooting_Percentage",  # Maps ts_percent to True_Shooting_Percentage
    "e_fg_percent": "Effective_Field_Goal_Percentage",  # Maps e_fg_percent to Effective_Field_Goal_Percentage
    "tov_percent": "Turnover_Percentage",  # Maps tov_percent to Turnover_Percentage
    "orb_percent": "Offensive_Rebound_Percentage",  # Maps orb_percent to Offensive_Rebound_Percentage
    "ft_fga": "Free_Throws_Per_FGA",  # Maps ft_fga to Free_Throws_Per_FGA
    "opp_e_fg_percent": "Opponent_EFG_Percentage",  # Maps opp_e_fg_percent to Opponent_EFG_Percentage
    "opp_tov_percent": "Opponent_Turnover_Percentage",  # Maps opp_tov_percent to Opponent_Turnover_Percentage
    "opp_drb_percent": "Opponent_Defensive_Rebound_Percentage",  # Maps opp_drb_percent to Opponent_Defensive_Rebound_Percentage
    "opp_ft_fga": "Opponent_Free_Throws_Per_FGA",  # Maps opp_ft_fga to Opponent_Free_Throws_Per_FGA
    "arena": "Arena",  # Maps arena to Arena
    "attend": "Attendance",  # Maps attend to Attendance
    "attend_g": "Attendance_Per_Game",  # Maps attend_g to Attendance_Per_Game
}
# Filter out columns set to None in the mapping
valid_columns = {old: new for old, new in COLUMN_MAPPING.items() if new}

# Process all files in the directory

# Read the CSV file
filepath = "../nba-aba-baa-stats/Advanced.csv"

data = pd.read_csv(file_path)

# Map columns to match the database schema
data = data.rename(columns=valid_columns)

# Select only the valid columns
data = data[list(valid_columns.values())]

# Insert data into the database
data.to_sql("Game_Shots", engine, if_exists="append", index=False)
print(f"Inserted {len(data)} rows from {filename} into Game_Shots.")
