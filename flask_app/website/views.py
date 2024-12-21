from flask import Blueprint, render_template, request
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
    query = text("""
        SELECT *
        FROM Teams
        """)
    teams = db.session.execute(query).fetchall()

    return render_template("teams.html", teams=teams)

@views.route('/team_season_info', methods=['GET', 'POST'])
def team_season_info():
    all_teams = db.session.execute(text("""
            SELECT *
            FROM Teams
        """)).fetchall()

    selected_team = None
    results = []

    if request.method == 'POST':
        selected_team = request.form.get('team')
        print(selected_team)
        if selected_team:
            query = text("""
                SELECT
                    team_id,
                    Seasons.year as year,
                    league,
                    abbreviation,
                    w as wins,
                    l as losses,
                    pw as playoff_wins,
                    pl as playoff_losses,
                    age
                FROM Team_Season_Info
                RIGHT JOIN Seasons ON Seasons.season_id = Team_Season_Info.season_id
                WHERE team_id = :team_id 
            """)
            results = db.session.execute(query, {'team_id': selected_team}).fetchall()
        else:
            results = []
    return render_template("team_season_info.html", teams=all_teams, results=results)

@views.route('/seasons')
def seasons():
    return render_template("seasons.html")