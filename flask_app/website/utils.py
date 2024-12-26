from sqlalchemy import text
from .views import db

def validate_player_data(player_name, birth_year, num_seasons, first_seas, last_seas, mvp_total):
  if not player_name or player_name.strip() == "":
    return False, 'Player Name cannot be empty'
  
  if birth_year and (int(birth_year) < 1800 or int(birth_year) > 2025):
    return False, 'Birth Year must be between 1800 and 2025'

  if num_seasons and (not num_seasons.isdigit() or int(num_seasons) <= 0):
    return False, 'Number of seasons must be greater than 0'
  
  if first_seas and last_seas and int(num_seasons) != int(last_seas) - int(first_seas) + 1:
    return False, 'Number of seasons must be correct with regard to first and last season'

  if first_seas and last_seas and first_seas > last_seas:
    return False, 'First Season cannot be later than Last Season'
  
  if mvp_total == '':
    mvp_total = None
  
  if mvp_total and int(mvp_total) < 0:
    return False, 'MVP Total cannot be negative'
  
  return True, None

def validate_team_data(team_name, abbreviations):
  if not team_name or team_name.strip() == "":
    return False, 'Team Name cannot be empty'
  
  if not abbreviations or abbreviations.strip() == "":
    return False, 'Abbreviations cannot be empty'

  return True, None

def validate_player_stats(season_id, player_id):
  season_exists_query = text("SELECT COUNT(*) FROM Seasons WHERE season_id = :season_id")
  result_season = db.session.execute(season_exists_query, {"season_id": season_id}).scalar()

  if result_season == 0:
    return False, 'Season ID does not exist'
  
  player_exists_query = text("SELECT COUNT(*) FROM Players WHERE Player_ID = :player_id")
  result_player = db.session.execute(player_exists_query, {"player_id": player_id}).scalar()

  if result_player == 0:
    return False, 'Player ID does not exist'
  
  return True, None


def validate_player_info(season_id, player_id, team_id, age, experience):
  season_exists_query = text("SELECT COUNT(*) FROM Seasons WHERE season_id = :season_id")
  result_season = db.session.execute(season_exists_query, {"season_id": season_id}).scalar()

  if result_season == 0:
    return False, 'Season ID does not exist'
  
  player_exists_query = text("SELECT COUNT(*) FROM Players WHERE Player_ID = :player_id")
  result_player = db.session.execute(player_exists_query, {"player_id": player_id}).scalar()

  if result_player == 0:
    return False, 'Player ID does not exist'
  
  team_exists_query = text("SELECT COUNT(*) FROM Teams WHERE Team_ID = :team_id")
  result_team = db.session.execute(team_exists_query, {"team_id": team_id}).scalar()

  if result_team == 0:
    return False, 'Team ID does not exist'

  if age and int(age) < 0:
    return False, 'Age cannot be negative'
  
  if experience and int(experience) < 0:
    return False, 'Experience cannot be negative'

  return True, None