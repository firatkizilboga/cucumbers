from flask import Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Import text for raw SQL queries

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
    """)

    # Execute the query and fetch all rows
    players = db.session.execute(query).fetchall()
    print(players)

    return render_template("players.html", players=players)

@views.route('/player_season_stats')
def player_season_stats():
    return render_template("player_season_stats.html")

@views.route('/player_season_info')
def player_season_info():
    return render_template("player_season_info.html")

@views.route('/teams')
def teams():
    return render_template("teams.html")

@views.route('/seasons')
def seasons():
    query = text("""
    SELECT * 
    FROM Seasons ;
    """)

    # Execute the query and fetch all rows
    seasons= db.session.execute(query).fetchall()
    return render_template("seasons.html", seasons=seasons)
