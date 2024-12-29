from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from sqlalchemy import text
import csv
import io
import json
import pandas as pd
import plotly.express as px
import plotly
from flask_caching import Cache

views = Blueprint("views", __name__)
db = SQLAlchemy()
cache = Cache()

from sqlalchemy import text  # Import text for raw SQL queries
from .utils import validate_player_data, validate_player_stats, validate_player_info
from .auth import admin_required

from flask_login import login_user, logout_user, login_required, current_user


@views.route("/")
def homepage():
    return render_template("home.html")


@views.route("/profile")
@login_required
def profile():
    return (
        f"This is {current_user.username}'s profile! Only logged in users can see this."
    )


@views.route("/admin-page")
@admin_required
def admin_page():
    if not current_user.is_admin:
        flash("You do not have permission to view this page.", category="error")
        return redirect(url_for("views.homepage"))
    return "Welcome to the admin page!"


# -----------------------
# Players views
# -----------------------


@views.route("/players")
def players():
    query = text("""
    SELECT * 
    FROM Players
    LIMIT 3
    """)

    # Execute the query and fetch all rows
    players = db.session.execute(query).fetchall()

    return render_template("players.html", players=players)


@views.route("/add_player", methods=["GET", "POST"])
@admin_required
def add_player():
    if request.method == "POST":
        # Get the form values for the new player
        player_name = request.form.get("Player")
        birth_year = request.form.get("Birth_Year")
        num_seasons = request.form.get("Num_Seasons")
        first_seas = request.form.get("First_Seas")
        last_seas = request.form.get("Last_Seas")
        mvp_total = request.form.get("MVP_Total")
        hof = True if request.form.get("HOF") == "on" else False

        if mvp_total == "":
            mvp_total = None
        if birth_year == "":
            birth_year = None
        if num_seasons == "":
            num_seasons = None
        if first_seas == "":
            first_seas = None
        if last_seas == "":
            last_seas = None

        is_valid, error_message = validate_player_data(
            player_name, birth_year, num_seasons, first_seas, last_seas, mvp_total
        )

        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("views.add_player"))

        query_max_id = text("SELECT MAX(Player_ID) FROM Players")
        max_player_id = db.session.execute(query_max_id).scalar()
        new_player_id = max_player_id + 1 if max_player_id else 1

        query_insert = text("""
                INSERT INTO Players (Player_ID, Player, Birth_Year, Num_Seasons, First_Seas, Last_Seas, MVP_Total, HOF)
                VALUES (:player_id, :player_name, :birth_year, :num_seasons, :first_seas, :last_seas, :mvp_total, :hof)
            """)

        db.session.execute(
            query_insert,
            {
                "player_id": new_player_id,
                "player_name": player_name,
                "birth_year": birth_year,
                "num_seasons": num_seasons,
                "first_seas": first_seas,
                "last_seas": last_seas,
                "mvp_total": mvp_total,
                "hof": hof,
            },
        )
        db.session.commit()

        flash("Player added successfully!", "success")
        return redirect(url_for("views.players"))

    return render_template("add_player.html")


@views.route("/delete_player/<int:player_id>", methods=["POST"])
@admin_required
def delete_player(player_id):
    # Execute the DELETE SQL query directly
    query = text("DELETE FROM Players WHERE Player_ID = :player_id")
    db.session.execute(query, {"player_id": player_id})

    db.session.commit()

    return redirect(url_for("views.players"))


@views.route("/edit_player/<int:player_id>", methods=["GET", "POST"])
@admin_required
def edit_player(player_id):
    # Retrieve the player's details
    query = text("SELECT * FROM Players WHERE Player_ID = :player_id")
    player = db.session.execute(query, {"player_id": player_id}).fetchone()

    if request.method == "POST":
        # Get updated values from the form
        player_name = request.form.get("Player")
        birth_year = request.form.get("Birth_Year")
        num_seasons = request.form.get("Num_Seasons")
        first_seas = request.form.get("First_Seas")
        last_seas = request.form.get("Last_Seas")
        mvp_total = request.form.get("MVP_Total")
        hof = True if request.form.get("HOF") == "on" else False

        if mvp_total == "":
            mvp_total = None
        if birth_year == "":
            birth_year = None
        if num_seasons == "":
            num_seasons = None
        if first_seas == "":
            first_seas = None
        if last_seas == "":
            last_seas = None

        is_valid, error_message = validate_player_data(
            player_name, birth_year, num_seasons, first_seas, last_seas, mvp_total
        )

        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("views.edit_player", player_id=player_id))

        # Update the player's details in the database
        query_update = text("""
            UPDATE Players
            SET Player = :player_name,
                Birth_Year = :birth_year,
                Num_Seasons = :num_seasons,
                First_Seas = :first_seas,
                Last_Seas = :last_seas,
                MVP_Total = :mvp_total,
                HOF = :hof
            WHERE Player_ID = :player_id
        """)

        db.session.execute(
            query_update,
            {
                "player_name": player_name,
                "birth_year": birth_year,
                "num_seasons": num_seasons,
                "first_seas": first_seas,
                "last_seas": last_seas,
                "mvp_total": mvp_total,
                "hof": hof,
                "player_id": player_id,
            },
        )
        db.session.commit()

        return redirect(url_for("views.players"))

    return render_template("edit_player.html", player=player)


@views.route("/player_season_stats")
def player_season_stats():
    query = text("""
    SELECT * 
    FROM Player_Season_Stats
    LIMIT 3
    """)

    # Execute the query and fetch all rows
    player_season_stats = db.session.execute(query).fetchall()

    return render_template("player_season_stats.html", stats=player_season_stats)


@views.route("/add_player_season_stats", methods=["GET", "POST"])
@admin_required
def add_player_season_stats():
    if request.method == "POST":
        # Get values from the form
        season_id = request.form.get("Season_ID")
        player_id = request.form.get("Player_ID")
        games = request.form.get("Games")
        per = request.form.get("PER")
        ts_percent = request.form.get("TS_Percent")
        x3p_ar = request.form.get("X3p_ar")
        f_tr = request.form.get("F_tr")
        orb_percent = request.form.get("ORB_Percent")
        drb_percent = request.form.get("DRB_Percent")
        trb_percent = request.form.get("TRB_Percent")
        ast_percent = request.form.get("AST_Percent")
        stl_percent = request.form.get("STL_Percent")
        blk_percent = request.form.get("BLK_Percent")
        tov_percent = request.form.get("TOV_Percent")
        usg_percent = request.form.get("USG_Percent")
        ows = request.form.get("OWS")
        dws = request.form.get("DWS")
        ws = request.form.get("WS")
        ws_48 = request.form.get("WS_48")
        obpm = request.form.get("OBPM")
        dbpm = request.form.get("DBPM")
        bpm = request.form.get("BPM")
        vorp = request.form.get("VORP")

        variables = [
            season_id,
            player_id,
            games,
            per,
            ts_percent,
            x3p_ar,
            f_tr,
            orb_percent,
            drb_percent,
            trb_percent,
            ast_percent,
            stl_percent,
            blk_percent,
            tov_percent,
            usg_percent,
            ows,
            dws,
            ws,
            ws_48,
            obpm,
            dbpm,
            bpm,
            vorp,
        ]

        for i, value in enumerate(variables):
            if value == "":
                variables[i] = None

        (
            season_id,
            player_id,
            games,
            per,
            ts_percent,
            x3p_ar,
            f_tr,
            orb_percent,
            drb_percent,
            trb_percent,
            ast_percent,
            stl_percent,
            blk_percent,
            tov_percent,
            usg_percent,
            ows,
            dws,
            ws,
            ws_48,
            obpm,
            dbpm,
            bpm,
            vorp,
        ) = variables

        is_valid, error_message = validate_player_stats(season_id, player_id)

        if not is_valid:
            flash(error_message, "danger")
            return render_template("add_player_season_stats.html")

        # Insert new player season stats into the database
        query_insert = text("""
            INSERT INTO Player_Season_Stats (
                Season_ID, Player_ID, Games, PER, TS_Percent, X3p_ar, F_tr, ORB_Percent, DRB_Percent, TRB_Percent, AST_Percent, 
                STL_Percent, BLK_Percent, TOV_Percent, USG_Percent, OWS, DWS, WS, WS_48, OBPM, DBPM, BPM, VORP
            ) VALUES (
                :season_id, :player_id, :games, :per, :ts_percent, :x3p_ar, :f_tr, :orb_percent, :drb_percent, :trb_percent, :ast_percent, 
                :stl_percent, :blk_percent, :tov_percent, :usg_percent, :ows, :dws, :ws, :ws_48, :obpm, :dbpm, :bpm, :vorp
            )
        """)

        db.session.execute(
            query_insert,
            {
                "season_id": season_id,
                "player_id": player_id,
                "games": games,
                "per": per,
                "ts_percent": ts_percent,
                "x3p_ar": x3p_ar,
                "f_tr": f_tr,
                "orb_percent": orb_percent,
                "drb_percent": drb_percent,
                "trb_percent": trb_percent,
                "ast_percent": ast_percent,
                "stl_percent": stl_percent,
                "blk_percent": blk_percent,
                "tov_percent": tov_percent,
                "usg_percent": usg_percent,
                "ows": ows,
                "dws": dws,
                "ws": ws,
                "ws_48": ws_48,
                "obpm": obpm,
                "dbpm": dbpm,
                "bpm": bpm,
                "vorp": vorp,
            },
        )
        db.session.commit()

        flash("New Player Season Stats added successfully", "success")
        return redirect(url_for("views.player_season_stats"))

    return render_template("add_player_season_stats.html")


@views.route(
    "/delete_player_season_stats/<int:season_id>/<int:player_id>", methods=["POST"]
)
@admin_required
def delete_player_season_stats(season_id, player_id):
    # Execute the DELETE SQL query using both Season_ID and Player_ID
    query = text("""
        DELETE FROM Player_Season_Stats
        WHERE Season_ID = :season_id AND Player_ID = :player_id
    """)
    db.session.execute(query, {"season_id": season_id, "player_id": player_id})

    db.session.commit()

    return redirect(url_for("views.player_season_stats"))


@views.route(
    "/edit_player_season_stats/<int:season_id>/<int:player_id>", methods=["GET", "POST"]
)
@admin_required
def edit_player_season_stats(season_id, player_id):
    # Retrieve the player season stats details
    query = text(
        "SELECT * FROM Player_Season_Stats WHERE Season_ID = :season_id AND Player_ID = :player_id"
    )
    stats = db.session.execute(
        query, {"season_id": season_id, "player_id": player_id}
    ).fetchone()

    if request.method == "POST":
        # Get updated values from the form
        games = request.form.get("Games")
        per = request.form.get("PER")
        ts_percent = request.form.get("TS_Percent")
        x3p_ar = request.form.get("X3p_ar")
        f_tr = request.form.get("F_tr")
        orb_percent = request.form.get("ORB_Percent")
        drb_percent = request.form.get("DRB_Percent")
        trb_percent = request.form.get("TRB_Percent")
        ast_percent = request.form.get("AST_Percent")
        stl_percent = request.form.get("STL_Percent")
        blk_percent = request.form.get("BLK_Percent")
        tov_percent = request.form.get("TOV_Percent")
        usg_percent = request.form.get("USG_Percent")
        ows = request.form.get("OWS")
        dws = request.form.get("DWS")
        ws = request.form.get("WS")
        ws_48 = request.form.get("WS_48")
        obpm = request.form.get("OBPM")
        dbpm = request.form.get("DBPM")
        bpm = request.form.get("BPM")
        vorp = request.form.get("VORP")

        variables = [
            games,
            per,
            ts_percent,
            x3p_ar,
            f_tr,
            orb_percent,
            drb_percent,
            trb_percent,
            ast_percent,
            stl_percent,
            blk_percent,
            tov_percent,
            usg_percent,
            ows,
            dws,
            ws,
            ws_48,
            obpm,
            dbpm,
            bpm,
            vorp,
        ]

        for i, value in enumerate(variables):
            if value == "":
                variables[i] = None

        (
            games,
            per,
            ts_percent,
            x3p_ar,
            f_tr,
            orb_percent,
            drb_percent,
            trb_percent,
            ast_percent,
            stl_percent,
            blk_percent,
            tov_percent,
            usg_percent,
            ows,
            dws,
            ws,
            ws_48,
            obpm,
            dbpm,
            bpm,
            vorp,
        ) = variables

        # Update the player season stats in the database
        query_update = text("""
            UPDATE Player_Season_Stats
            SET Games = :games,
                PER = :per,
                TS_Percent = :ts_percent,
                X3p_ar = :x3p_ar,
                F_tr = :f_tr,
                ORB_Percent = :orb_percent,
                DRB_Percent = :drb_percent,
                TRB_Percent = :trb_percent,
                AST_Percent = :ast_percent,
                STL_Percent = :stl_percent,
                BLK_Percent = :blk_percent,
                TOV_Percent = :tov_percent,
                USG_Percent = :usg_percent,
                OWS = :ows,
                DWS = :dws,
                WS = :ws,
                WS_48 = :ws_48,
                OBPM = :obpm,
                DBPM = :dbpm,
                BPM = :bpm,
                VORP = :vorp
            WHERE Season_ID = :season_id AND Player_ID = :player_id
        """)

        db.session.execute(
            query_update,
            {
                "games": games,
                "per": per,
                "ts_percent": ts_percent,
                "x3p_ar": x3p_ar,
                "f_tr": f_tr,
                "orb_percent": orb_percent,
                "drb_percent": drb_percent,
                "trb_percent": trb_percent,
                "ast_percent": ast_percent,
                "stl_percent": stl_percent,
                "blk_percent": blk_percent,
                "tov_percent": tov_percent,
                "usg_percent": usg_percent,
                "ows": ows,
                "dws": dws,
                "ws": ws,
                "ws_48": ws_48,
                "obpm": obpm,
                "dbpm": dbpm,
                "bpm": bpm,
                "vorp": vorp,
                "season_id": season_id,
                "player_id": player_id,
            },
        )
        db.session.commit()

        flash("Player Season Stats updated successfully", "success")
        return redirect(
            url_for(
                "views.player_season_stats", season_id=season_id, player_id=player_id
            )
        )

    return render_template("edit_player_season_stats.html", stats=stats)


@views.route("/player_season_info")
def player_season_info():
    query = text("""
    SELECT * 
    FROM Player_Info_Per_Season
    LIMIT 3
    """)

    # Execute the query and fetch all rows
    player_season_info = db.session.execute(query).fetchall()

    return render_template("player_season_info.html", information=player_season_info)


@views.route("/add_player_season_info", methods=["GET", "POST"])
@admin_required
def add_player_season_info():
    if request.method == "POST":
        # Get the form data
        season_id = request.form.get("Season_ID")
        player_id = request.form.get("Player_ID")
        player_name = request.form.get("Player_Name")
        league = request.form.get("League")
        team_id = request.form.get("Team_ID")
        position = request.form.get("Position")
        age = request.form.get("Age")
        experience = request.form.get("Experience")
        mvp = request.form.get("MVP") == "True"

        if age == "":
            age = None
        if experience == "":
            experience = None

        is_valid, error_message = validate_player_info(
            season_id, player_id, team_id, age, experience
        )

        if not is_valid:
            flash(error_message, "danger")
            return render_template("add_player_season_info.html")

        # Insert the new player season info into the database
        query_insert = text("""
            INSERT INTO Player_Info_Per_Season (Season_ID, Player_ID, Player_Name, League, Team_ID, Position, Age, Experience, MVP)
            VALUES (:season_id, :player_id, :player_name, :league, :team_id, :position, :age, :experience, :mvp)
        """)

        db.session.execute(
            query_insert,
            {
                "season_id": season_id,
                "player_id": player_id,
                "player_name": player_name,
                "league": league,
                "team_id": team_id,
                "position": position,
                "age": age,
                "experience": experience,
                "mvp": mvp,
            },
        )
        db.session.commit()

        return redirect(url_for("views.player_season_info"))

    return render_template("add_player_season_info.html")


@views.route(
    "/delete_player_season_info/<int:season_id>/<int:player_id>", methods=["POST"]
)
@admin_required
def delete_player_season_info(season_id, player_id):
    # Execute the DELETE SQL query directly
    query = text("""
        DELETE FROM Player_Info_Per_Season
        WHERE Season_ID = :season_id AND Player_ID = :player_id
    """)
    db.session.execute(query, {"season_id": season_id, "player_id": player_id})

    db.session.commit()

    return redirect(url_for("views.player_season_info"))


@views.route(
    "/edit_player_season_info/<int:season_id>/<int:player_id>", methods=["GET", "POST"]
)
@admin_required
def edit_player_season_info(season_id, player_id):
    # Retrieve the player season info details
    query = text("""
        SELECT * FROM Player_Info_Per_Season 
        WHERE Season_ID = :season_id AND Player_ID = :player_id
    """)
    info = db.session.execute(
        query, {"season_id": season_id, "player_id": player_id}
    ).fetchone()

    if request.method == "POST":
        # Get updated values from the form
        player_name = request.form.get("Player_Name")
        league = request.form.get("League")
        team_id = request.form.get("Team_ID")
        position = request.form.get("Position")
        age = request.form.get("Age")
        experience = request.form.get("Experience")
        mvp = request.form.get("MVP") == "True"  # Convert to boolean

        if age == "":
            age = None
        if experience == "":
            experience = None

        is_valid, error_message = validate_player_info(
            season_id, player_id, team_id, age, experience
        )

        if not is_valid:
            flash(error_message, "danger")
            return render_template("edit_player_season_info.html", info=info)

        # Update the player season info in the database
        query_update = text("""
            UPDATE Player_Info_Per_Season
            SET Player_Name = :player_name,
                League = :league,
                Team_ID = :team_id,
                Position = :position,
                Age = :age,
                Experience = :experience,
                MVP = :mvp
            WHERE Season_ID = :season_id AND Player_ID = :player_id
        """)

        db.session.execute(
            query_update,
            {
                "player_name": player_name,
                "league": league,
                "team_id": team_id,
                "position": position,
                "age": age,
                "experience": experience,
                "mvp": mvp,
                "season_id": season_id,
                "player_id": player_id,
            },
        )
        db.session.commit()

        return redirect(url_for("views.player_season_info"))

    return render_template("edit_player_season_info.html", info=info)


# -----------------------
# Teams views
# -----------------------


@views.route("/teams")
def teams():
    query = text("""
        SELECT *
        FROM Teams
        """)
    teams = db.session.execute(query).fetchall()

    return render_template("teams.html", teams=teams)


@views.route("/team_season_info", methods=["GET", "POST"])
def team_season_info():
    all_teams = db.session.execute(
        text("""
            SELECT *
            FROM Teams
        """)
    ).fetchall()

    selected_team = None
    results = []

    if request.method == "POST":
        selected_team = request.form.get("team")
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
            results = db.session.execute(query, {"team_id": selected_team}).fetchall()
        else:
            results = []
    return render_template("team_season_info.html", teams=all_teams, results=results)


# -----------------------
# Seasons & Game Shots views
# -----------------------


@views.route("/seasons")
def seasons():
    query = text("""
    SELECT * 
    FROM Seasons ;
    """)

    # Execute the query and fetch all rows
    seasons = db.session.execute(query).fetchall()
    return render_template("seasons.html", seasons=seasons)


@views.route("/delete_season/<int:season_id>", methods=["POST"])
@admin_required
def delete_season(season_id):
    try:
        query = text("DELETE FROM Seasons WHERE season_id = :season_id")
        db.session.execute(query, {"season_id": season_id})
        db.session.commit()
        flash("Season deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the season.", "error")
    return redirect(url_for("views.seasons"))


# Edit Season
@views.route("/edit_season/<int:season_id>", methods=["GET", "POST"])
@admin_required
def edit_season(season_id):
    query = text("SELECT * FROM Seasons WHERE season_id = :season_id")
    season = db.session.execute(query, {"season_id": season_id}).fetchone()
    if not season:
        flash("Season not found.", "error")
        return redirect(url_for("views.seasons"))
    if request.method == "POST":
        year = request.form.get("Year")
        winner_team_id = request.form.get("Winner_Team_ID")
        num_players = request.form.get("Num_Players")
        num_teams = request.form.get("Num_Teams")
        if not year or not winner_team_id:
            flash("Year and Winner Team ID are required.", "error")
            return redirect(url_for("views.edit_season", season_id=season_id))
        try:
            year = int(year)
            winner_team_id = int(winner_team_id)
            num_players = int(num_players) if num_players else None
            num_teams = int(num_teams) if num_teams else None
        except ValueError:
            flash("Invalid input. Please enter valid numbers.", "error")
            return redirect(url_for("views.edit_season", season_id=season_id))
        try:
            query_update = text("""
                UPDATE Seasons
                SET year = :year,
                    season_winner_team_id = :winner_team_id,
                    num_players_in_season = :num_players,
                    num_teams_in_season = :num_teams
                WHERE season_id = :season_id
            """)
            db.session.execute(
                query_update,
                {
                    "year": year,
                    "winner_team_id": winner_team_id,
                    "num_players": num_players,
                    "num_teams": num_teams,
                    "season_id": season_id,
                },
            )
            db.session.commit()
            flash("Season updated successfully.", "success")
            return redirect(url_for("views.seasons"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the season.", "error")
    return render_template("edit_season.html", season=season)


# Add Season (Optional)
@views.route("/add_season", methods=["GET", "POST"])
@admin_required
def add_season():
    if not current_user.is_admin:
        abort(403)
    if request.method == "POST":
        year = request.form.get("Year")
        winner_team_id = request.form.get("Winner_Team_ID")
        num_players = request.form.get("Num_Players")
        num_teams = request.form.get("Num_Teams")
        if not year or not winner_team_id:
            flash("Year and Winner Team ID are required.", "error")
            return redirect(url_for("views.add_season"))
        try:
            year = int(year)
            winner_team_id = int(winner_team_id)
            num_players = int(num_players) if num_players else None
            num_teams = int(num_teams) if num_teams else None
        except ValueError:
            flash("Invalid input. Please enter valid numbers.", "error")
            return redirect(url_for("views.add_season"))
        try:
            query_insert = text("""
                INSERT INTO Seasons (year, season_winner_team_id, num_players_in_season, num_teams_in_season)
                VALUES (:year, :winner_team_id, :num_players, :num_teams)
            """)
            db.session.execute(
                query_insert,
                {
                    "year": year,
                    "winner_team_id": winner_team_id,
                    "num_players": num_players,
                    "num_teams": num_teams,
                },
            )
            db.session.commit()
            flash("Season added successfully.", "success")
            return redirect(url_for("views.seasons"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while adding the season.", "error")
    return render_template("add_season.html")


@views.route("/manage_game_shots", methods=["GET"])
@admin_required
def manage_game_shots():
    # Fetch all Game_Shots to display
    game_shots_query = text("SELECT * FROM Game_Shots limit 100;")
    game_shots = db.session.execute(game_shots_query).fetchall()

    # Fetch all Seasons for the Season_ID dropdown
    seasons_query = text("SELECT Season_ID, year FROM Seasons ORDER BY year DESC")
    seasons = db.session.execute(seasons_query).fetchall()

    return render_template(
        "manage_game_shots.html", game_shots=game_shots, seasons=seasons
    )


@views.route("/upload_game_shots", methods=["POST"])
@admin_required
def upload_game_shots():
    if "insert_file" not in request.files:
        flash("No file part for insertion.", "error")
        return redirect(url_for("views.manage_game_shots"))

    file = request.files["insert_file"]
    if file.filename == "":
        flash("No file selected for insertion.", "error")
        return redirect(url_for("views.manage_game_shots"))

    if not file.filename.lower().endswith(".csv"):
        flash("Invalid file format for insertion. Please upload a CSV file.", "error")
        return redirect(url_for("views.manage_game_shots"))

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)

        expected_columns = {
            "Game_ID",
            "Season_ID",
            "Team_ID",
            "Player_ID",
            "Position_Group",
            "Position",
            "Game_Date",
            "Home_Team",
            "Away_Team",
            "Event_Type",
            "Shot_Made",
            "Action_Type",
            "Shot_Type",
            "Basic_Zone",
            "Zone_Name",
            "Zone_Abb",
            "Zone_Range",
            "Loc_X",
            "Loc_Y",
            "Shot_Distance",
            "Quarter",
            "Mins_Left",
            "Secs_Left",
        }
        if not expected_columns.issubset(set(csv_input.fieldnames)):
            flash("CSV file is missing required columns for insertion.", "error")
            return redirect(url_for("views.manage_game_shots"))

        insert_query = text("""
            INSERT INTO Game_Shots (
                Game_ID, Season_ID, Team_ID, Player_ID, Position_Group, Position,
                Game_Date, Home_Team, Away_Team, Event_Type, Shot_Made, Action_Type,
                Shot_Type, Basic_Zone, Zone_Name, Zone_Abb, Zone_Range,
                Loc_X, Loc_Y, Shot_Distance, Quarter, Mins_Left, Secs_Left
            ) VALUES (
                :Game_ID, :Season_ID, :Team_ID, :Player_ID, :Position_Group, :Position,
                :Game_Date, :Home_Team, :Away_Team, :Event_Type, :Shot_Made, :Action_Type,
                :Shot_Type, :Basic_Zone, :Zone_Name, :Zone_Abb, :Zone_Range,
                :Loc_X, :Loc_Y, :Shot_Distance, :Quarter, :Mins_Left, :Secs_Left
            )
        """)

        rows_inserted = 0
        for row in csv_input:
            # Data validation and type conversion
            try:
                data = {
                    "Game_ID": int(row["Game_ID"]),
                    "Season_ID": int(row["Season_ID"]),
                    "Team_ID": int(row["Team_ID"]),
                    "Player_ID": int(row["Player_ID"]),
                    "Position_Group": row["Position_Group"],
                    "Position": row["Position"],
                    "Game_Date": row["Game_Date"],  # Ensure correct date format
                    "Home_Team": row["Home_Team"],
                    "Away_Team": row["Away_Team"],
                    "Event_Type": row["Event_Type"],
                    "Shot_Made": row["Shot_Made"].strip().lower()
                    in ["true", "1", "yes"],
                    "Action_Type": row["Action_Type"],
                    "Shot_Type": row["Shot_Type"],
                    "Basic_Zone": row["Basic_Zone"],
                    "Zone_Name": row["Zone_Name"],
                    "Zone_Abb": row["Zone_Abb"],
                    "Zone_Range": row["Zone_Range"],
                    "Loc_X": float(row["Loc_X"]),
                    "Loc_Y": float(row["Loc_Y"]),
                    "Shot_Distance": float(row["Shot_Distance"]),
                    "Quarter": int(row["Quarter"]),
                    "Mins_Left": int(row["Mins_Left"]),
                    "Secs_Left": int(row["Secs_Left"]),
                }

                db.session.execute(insert_query, data)
                rows_inserted += 1
            except Exception as e:
                db.session.rollback()
                flash(f"Error inserting row: {e}", "error")
                return redirect(url_for("views.manage_game_shots"))

        db.session.commit()
        flash(f"Successfully inserted {rows_inserted} rows into Game_Shots.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during insertion: {e}", "error")

    return redirect(url_for("views.manage_game_shots"))


@views.route("/update_game_shots", methods=["POST"])
@admin_required
def update_game_shots():
    if "update_file" not in request.files:
        flash("No file part for updating.", "error")
        return redirect(url_for("views.manage_game_shots"))

    file = request.files["update_file"]
    if file.filename == "":
        flash("No file selected for updating.", "error")
        return redirect(url_for("views.manage_game_shots"))

    if not file.filename.lower().endswith(".csv"):
        flash("Invalid file format for updating. Please upload a CSV file.", "error")
        return redirect(url_for("views.manage_game_shots"))

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)

        expected_columns = {
            "shot_id",
            "Game_ID",
            "Season_ID",
            "Team_ID",
            "Player_ID",
            "Position_Group",
            "Position",
            "Game_Date",
            "Home_Team",
            "Away_Team",
            "Event_Type",
            "Shot_Made",
            "Action_Type",
            "Shot_Type",
            "Basic_Zone",
            "Zone_Name",
            "Zone_Abb",
            "Zone_Range",
            "Loc_X",
            "Loc_Y",
            "Shot_Distance",
            "Quarter",
            "Mins_Left",
            "Secs_Left",
        }

        print(csv_input.fieldnames)
        if not expected_columns.issubset(set(csv_input.fieldnames)):
            flash(
                f"CSV file is missing required columns for updating. {expected_columns - set(csv_input.fieldnames)}",
                "error",
            )
            return redirect(url_for("views.manage_game_shots"))

        update_query = text("""
            UPDATE Game_Shots SET
                Game_ID = :Game_ID,
                Season_ID = :Season_ID,
                Team_ID = :Team_ID,
                Player_ID = :Player_ID,
                Position_Group = :Position_Group,
                Position = :Position,
                Game_Date = :Game_Date,
                Home_Team = :Home_Team,
                Away_Team = :Away_Team,
                Event_Type = :Event_Type,
                Shot_Made = :Shot_Made,
                Action_Type = :Action_Type,
                Shot_Type = :Shot_Type,
                Basic_Zone = :Basic_Zone,
                Zone_Name = :Zone_Name,
                Zone_Abb = :Zone_Abb,
                Zone_Range = :Zone_Range,
                Loc_X = :Loc_X,
                Loc_Y = :Loc_Y,
                Shot_Distance = :Shot_Distance,
                Quarter = :Quarter,
                Mins_Left = :Mins_Left,
                Secs_Left = :Secs_Left
            WHERE shot_id = :shot_id
        """)

        rows_updated = 0
        for row in csv_input:
            try:
                shot_id = int(row["shot_id"])
                data = {
                    "shot_id": shot_id,
                    "Game_ID": int(row["Game_ID"]),
                    "Season_ID": int(row["Season_ID"]),
                    "Team_ID": int(row["Team_ID"]),
                    "Player_ID": int(row["Player_ID"]),
                    "Position_Group": row["Position_Group"],
                    "Position": row["Position"],
                    "Game_Date": row["Game_Date"],  # Ensure correct date format
                    "Home_Team": row["Home_Team"],
                    "Away_Team": row["Away_Team"],
                    "Event_Type": row["Event_Type"],
                    "Shot_Made": row["Shot_Made"].strip().lower()
                    in ["true", "1", "yes"],
                    "Action_Type": row["Action_Type"],
                    "Shot_Type": row["Shot_Type"],
                    "Basic_Zone": row["Basic_Zone"],
                    "Zone_Name": row["Zone_Name"],
                    "Zone_Abb": row["Zone_Abb"],
                    "Zone_Range": row["Zone_Range"],
                    "Loc_X": float(row["Loc_X"]),
                    "Loc_Y": float(row["Loc_Y"]),
                    "Shot_Distance": float(row["Shot_Distance"]),
                    "Quarter": int(row["Quarter"]),
                    "Mins_Left": int(row["Mins_Left"]),
                    "Secs_Left": int(row["Secs_Left"]),
                }

                result = db.session.execute(update_query, data)
                if result.rowcount > 0:
                    rows_updated += result.rowcount
            except Exception as e:
                db.session.rollback()
                flash(
                    f"Error updating Shot_ID {row.get('Shot_ID', 'Unknown')}: {e}",
                    "error",
                )
                return redirect(url_for("views.manage_game_shots"))

        db.session.commit()
        flash(f"Successfully updated {rows_updated} rows in Game_Shots.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during updating: {e}", "error")

    return redirect(url_for("views.manage_game_shots"))


# views.py


@views.route("/delete_game_shots", methods=["POST"])
@admin_required
def delete_game_shots():
    # Retrieve form data
    shot_ids_str = request.form.get("delete_shot_ids")
    season_id = request.form.get("delete_season_id")

    # Validate Season_ID
    if not season_id:
        flash("No Season ID provided for deletion.", "error")
        return redirect(url_for("views.manage_game_shots"))

    try:
        season_id = int(season_id)
    except ValueError:
        flash("Invalid Season ID provided.", "error")
        return redirect(url_for("views.manage_game_shots"))

    # Validate Shot_IDs
    if not shot_ids_str:
        flash("No Shot_IDs provided for deletion.", "error")
        return redirect(url_for("views.manage_game_shots"))

    try:
        # Split the string and convert to integers, removing duplicates
        shot_ids = list(
            set(
                [
                    int(sid.strip())
                    for sid in shot_ids_str.split(",")
                    if sid.strip().isdigit()
                ]
            )
        )
        if not shot_ids:
            flash("No valid Shot_IDs provided for deletion.", "error")
            return redirect(url_for("views.manage_game_shots"))
    except Exception as e:
        flash(f"Error processing Shot_IDs: {e}", "error")
        return redirect(url_for("views.manage_game_shots"))

    try:
        # Verify that the Season_ID exists
        season_exists_query = text(
            "SELECT COUNT(*) FROM Seasons WHERE Season_ID = :season_id"
        )
        season_exists = db.session.execute(
            season_exists_query, {"season_id": season_id}
        ).scalar()
        if season_exists == 0:
            flash("The specified Season ID does not exist.", "error")
            return redirect(url_for("views.manage_game_shots"))

        # Perform the deletion
        delete_query = text("""
            DELETE FROM Game_Shots
            WHERE Shot_ID IN :shot_ids
              AND Season_ID = :season_id
        """)

        result = db.session.execute(
            delete_query, {"shot_ids": tuple(shot_ids), "season_id": season_id}
        )
        db.session.commit()

        # Provide feedback to the user
        flash(
            f"Successfully deleted {result.rowcount} Game Shot(s) from Season ID {season_id}.",
            "success",
        )
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during deletion: {e}", "error")

    return redirect(url_for("views.manage_game_shots"))


# Assuming 'db' and 'cache' are initialized elsewhere in your application


# Assuming 'db' and 'cache' are initialized elsewhere in your application


@views.route("/player_stats", methods=["GET", "POST"])
def player_stats():
    images = {}
    players = []
    seasons = []

    try:
        # Fetch all players
        players_query = text(
            "SELECT Player_ID, Player as PLAYER_NAME FROM Players ORDER BY PLAYER_NAME ASC"
        )
        players = db.session.execute(players_query).fetchall()

        # Fetch all seasons
        seasons_query = text("SELECT Season_ID, year FROM Seasons ORDER BY year DESC")
        seasons = db.session.execute(seasons_query).fetchall()
    except Exception as e:
        flash(f"Error fetching players or seasons: {e}", "error")
        return render_template(
            "player_stats.html", players=players, seasons=seasons, images=images
        )

    if request.method == "POST":
        selected_player_id = request.form.get("player")
        selected_season = request.form.get("season")

        if not selected_player_id or not selected_season:
            flash("Please select both a player and a season.", "error")
            return redirect(url_for("views.player_stats"))

        # Convert 'Lifetime' to None or handle appropriately
        if selected_season == "Lifetime":
            season_filter = None
        else:
            try:
                season_filter = int(selected_season)
            except ValueError:
                flash("Invalid season selected.", "error")
                return redirect(url_for("views.player_stats"))

        # Create a unique cache key based on player and season
        cache_key = f"player_{selected_player_id}_season_{season_filter if season_filter else 'Lifetime'}"
        cached_images = cache.get(cache_key)

        if cached_images:
            images = cached_images
        else:
            try:
                # Fetch shot data based on selection
                if season_filter:
                    shots_query = text("""
                        SELECT *
                        FROM Game_Shots
                        WHERE Player_ID = :player_id AND Season_ID = :season_id
                    """)
                    shots = db.session.execute(
                        shots_query,
                        {"player_id": selected_player_id, "season_id": season_filter},
                    ).fetchall()
                else:
                    shots_query = text("""
                        SELECT *
                        FROM Game_Shots
                        WHERE Player_ID = :player_id
                    """)
                    shots = db.session.execute(
                        shots_query, {"player_id": selected_player_id}
                    ).fetchall()

                # Convert to DataFrame using list of dicts
                shots_df = (
                    pd.DataFrame(
                        shots,
                        columns=[
                            "Game_ID",
                            "Season_ID",
                            "shot_id",
                            "Team_ID",
                            "Player_ID",
                            "Position_Group",
                            "Position",
                            "Game_Date",
                            "Home_Team",
                            "Away_Team",
                            "Event_Type",
                            "Shot_Made",
                            "Action_Type",
                            "Shot_Type",
                            "Basic_Zone",
                            "Zone_Name",
                            "Zone_Abb",
                            "Zone_Range",
                            "Loc_X",
                            "Loc_Y",
                            "Shot_Distance",
                            "Quarter",
                            "Mins_Left",
                            "Secs_Left",
                        ],
                    )
                    if shots
                    else pd.DataFrame()
                )

                if shots_df.empty:
                    flash(
                        "No shot data found for the selected player and season.", "info"
                    )
                    return render_template(
                        "player_stats.html",
                        players=players,
                        seasons=seasons,
                        images=images,
                    )

                # Generate visualizations using Plotly
                images["shot_map"] = generate_shot_map(shots_df)
                images["shot_histogram"] = generate_shot_histogram(shots_df)
                images["action_prob"] = generate_action_probability(shots_df)

                # Cache the images for future requests (cache for 1 hour)
                cache.set(cache_key, images, timeout=60 * 60)

            except Exception as e:
                flash(f"Error generating statistics: {e}", "error")

    return render_template(
        "player_stats.html", players=players, seasons=seasons, images=images
    )


def generate_shot_map(shots_df):
    """
    Generates an interactive Shot Map using Plotly Express with Loc_Y on the X-axis.
    """
    # Ensure the DataFrame is not empty
    if shots_df.empty:
        return {}

    # Create a scatter plot using Plotly Express with swapped axes
    fig = px.scatter(
        shots_df,
        x="Loc_Y",  # Swapped from Loc_X to Loc_Y
        y="Loc_X",  # Swapped from Loc_Y to Loc_X
        color="Shot_Made",
        color_discrete_map={True: "green", False: "red"},
        size_max=10,
        hover_data=["Action_Type", "Shot_Distance"],
        title="Shot Map (Side View)",
        labels={
            "Loc_Y": "Distance from Hoop",
            "Loc_X": "Left/Right Position",
            "Shot_Made": "Shot Made",
        },
    )

    # Define the basketball court dimensions using Plotly Graph Objects shapes
    court = create_court()

    # Add basketball court shapes to the figure
    for shape in court["shapes"]:
        fig.add_shape(shape)

    # Update layout to hide axes and grid, adjust ranges accordingly
    fig.update_layout(
        xaxis=dict(
            range=[0, 47.5],  # Adjusted X-axis range based on Loc_Y
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        ),
        yaxis=dict(
            range=[-25, 25],  # Adjusted Y-axis range based on Loc_X
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        ),
        plot_bgcolor="white",
        showlegend=True,
        xaxis_title="Distance from Hoop (Loc_Y)",
        yaxis_title="Left/Right Position (Loc_X)",
        hovermode="closest",
    )

    # Convert Plotly figure to JSON for embedding in HTML
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def generate_shot_histogram(shots_df):
    """
    Generates an interactive Shot Time Histogram using Plotly.
    """
    # Count shots per quarter, differentiating made and missed
    df_quarter = (
        shots_df.groupby(["Quarter", "Shot_Made"]).size().reset_index(name="Count")
    )

    # Create histogram
    fig = px.bar(
        df_quarter,
        x="Quarter",
        y="Count",
        color="Shot_Made",
        labels={
            "Shot_Made": "Shot Made",
            "Count": "Number of Shots",
            "Quarter": "Quarter",
        },
        title="Shots per Quarter",
        color_discrete_map={"True": "green", "False": "red"},
        barmode="stack",
    )

    fig.update_layout(
        xaxis=dict(tickmode="linear", dtick=1),
        yaxis=dict(title="Number of Shots"),
        legend_title_text="Shot Made",
    )

    # Convert Plotly figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def generate_action_probability(shots_df):
    """
    Generates an interactive Action Type Probability Bar Chart using Plotly.
    """
    # Calculate probability of making each action type
    df_action = shots_df.groupby("Action_Type")["Shot_Made"].mean().reset_index()
    df_action.rename(columns={"Shot_Made": "Probability"}, inplace=True)
    df_action.sort_values(by="Probability", ascending=False, inplace=True)

    # Create bar chart
    fig = px.bar(
        df_action,
        x="Probability",
        y="Action_Type",
        orientation="h",
        labels={
            "Probability": "Probability of Making Shot",
            "Action_Type": "Action Type",
        },
        title="Probability of Making Each Action Type",
        range_x=[0, 1],
        hover_data={"Probability": ":.2f"},
    )

    # Add probability labels
    fig.update_traces(marker_color="indigo")
    fig.update_layout(
        yaxis=dict(autorange="reversed"),  # Highest probability on top
        xaxis_tickformat=".0%",
    )

    # Convert Plotly figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def create_court():
    """
    Returns a dictionary containing shapes to draw a simplified basketball court with swapped axes.
    """
    court_shapes = [
        # Hoop
        dict(
            type="circle",
            xref="x",
            yref="y",
            x0=-0.75,
            y0=-0.75,
            x1=0.75,
            y1=0.75,
            line=dict(color="black", width=2),
        ),
        # Backboard
        dict(
            type="rect",
            xref="x",
            yref="y",
            x0=-0.75,  # Swapped from y to x
            y0=-3,  # Swapped from x to y
            x1=-0.65,  # Swapped from y to x
            y1=3,  # Swapped from x to y
            line=dict(color="black", width=2),
            fillcolor="black",
        ),
        # Paint
        dict(
            type="rect",
            xref="x",
            yref="y",
            x0=-19,  # Swapped from y to x
            y0=-8,  # Swapped from x to y
            x1=19,  # Swapped from y to x
            y1=8,  # Swapped from x to y
            line=dict(color="black", width=2),
        ),
        # Three-point line (arc)
        dict(
            type="circle",
            xref="x",
            yref="y",
            x0=-4.75,  # Adjusted for swapped axes
            y0=-23.75,
            x1=42.75,
            y1=23.75,
            line=dict(color="black", width=2),
            opacity=1,
            fillcolor="rgba(0,0,0,0)",
        ),
        # Restricted Area
        dict(
            type="circle",
            xref="x",
            yref="y",
            x0=-4,
            y0=-4,
            x1=4,
            y1=4,
            line=dict(color="black", width=2),
        ),
    ]

    return {"shapes": court_shapes}
