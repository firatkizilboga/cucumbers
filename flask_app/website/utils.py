def validate_player_data(birth_year, num_seasons, first_seas, last_seas, mvp_total):
  if birth_year and (int(birth_year) < 1800 or int(birth_year) > 2025):
    return False, 'Birth Year must be between 1800 and 2025'

  if num_seasons and (not num_seasons.isdigit() or int(num_seasons) <= 0):
    return False, 'Number of Seasons must be greater than 0'

  if first_seas and last_seas and first_seas > last_seas:
    return False, 'First Season cannot be later than Last Season'
  
  if mvp_total == '':
    mvp_total = None
  
  if mvp_total and int(mvp_total) < 0:
    return False, 'MVP Total cannot be negative'
  
  return True, None