from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def homepage():
    return render_template("home.html")

@views.route('/players')
def players():
    return render_template("players.html")

@views.route('/teams')
def teams():
    return render_template("teams.html")

@views.route('/seasons')
def seasons():
    return render_template("seasons.html")