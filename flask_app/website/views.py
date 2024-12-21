from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Import text for raw SQL queries
from .utils import validate_player_data

views = Blueprint('views', __name__)
db = SQLAlchemy()

@views.route('/')
def homepage():
    return render_template("home.html")

@views.route('/players')
def players():
    query = text("""
    SELECT * 
    FROM Players
    LIMIT 3
    """)

    # Execute the query and fetch all rows
    players = db.session.execute(query).fetchall()

    return render_template("players.html", players=players)

@views.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    # Execute the DELETE SQL query directly
    query = text('DELETE FROM Players WHERE Player_ID = :player_id')
    db.session.execute(query, {'player_id': player_id})
    
    db.session.commit()
    
    return redirect(url_for('views.players'))

@views.route('/edit_player/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    # Retrieve the player's details
    query = text('SELECT * FROM Players WHERE Player_ID = :player_id')
    player = db.session.execute(query, {'player_id': player_id}).fetchone()
    
    if request.method == 'POST':
        # Get updated values from the form
        player_name = request.form.get('Player')
        birth_year = request.form.get('Birth_Year')
        num_seasons = request.form.get('Num_Seasons')
        first_seas = request.form.get('First_Seas')
        last_seas = request.form.get('Last_Seas')
        mvp_total = request.form.get('MVP_Total')
        hof = True if request.form.get('HOF') == 'on' else False
        
        if mvp_total == '':
            mvp_total = None
        if birth_year == '':
            birth_year = None
        if num_seasons == '':
            num_seasons = None
        if first_seas == '':
            first_seas = None
        if last_seas == '':
            last_seas = None
        
        # Update the player's details in the database
        query_update = text('''
            UPDATE Players
            SET Player = :player_name,
                Birth_Year = :birth_year,
                Num_Seasons = :num_seasons,
                First_Seas = :first_seas,
                Last_Seas = :last_seas,
                MVP_Total = :mvp_total,
                HOF = :hof
            WHERE Player_ID = :player_id
        ''')
        
        is_valid, error_message = validate_player_data(birth_year, num_seasons, first_seas, last_seas, mvp_total)
        
        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('views.edit_player', player_id=player_id))
        
        db.session.execute(query_update, {
            'player_name': player_name,
            'birth_year': birth_year,
            'num_seasons': num_seasons,
            'first_seas': first_seas,
            'last_seas': last_seas,
            'mvp_total': mvp_total,
            'hof': hof,
            'player_id': player_id
        })
        db.session.commit()
        
        return redirect(url_for('views.players'))
    
    return render_template('edit_player.html', player=player)

@views.route('/player_season_stats')
def player_season_stats():
    query = text("""
    SELECT * 
    FROM Player_Season_Stats
    LIMIT 3
    """)

    # Execute the query and fetch all rows
    player_season_stats = db.session.execute(query).fetchall()
    
    return render_template("player_season_stats.html", stats=player_season_stats)

@views.route('/player_season_info')
def player_season_info():
    return render_template("player_season_info.html")

@views.route('/teams')
def teams():
    return render_template("teams.html")

@views.route('/seasons')
def seasons():
    return render_template("seasons.html")