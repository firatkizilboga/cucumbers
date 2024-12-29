from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from sqlalchemy import text
import csv
import io

views = Blueprint("views", __name__)
db = SQLAlchemy()

from sqlalchemy import text  # Import text for raw SQL queries
from .utils import validate_player_data, validate_player_stats, validate_player_info, validate_team_data
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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # Default to 10 rows per page
    search_query = request.args.get('search', None)

    if search_query:
        # If a search query is provided, fetch only the matching player
        query = text("""
        SELECT * 
        FROM Players
        WHERE Player LIKE :search
        """)
        players = db.session.execute(query, {"search": f"%{search_query}%"}).fetchall()
        total_pages = 1
    else:
        # Normal pagination logic
        offset = (page - 1) * per_page
        query = text("""
        SELECT * 
        FROM Players
        LIMIT :limit OFFSET :offset
        """)
        players = db.session.execute(query, {"limit": per_page, "offset": offset}).fetchall()

        # Calculate total page number
        total_players_query = text("SELECT COUNT(*) FROM Players")
        total_players = db.session.execute(total_players_query).scalar()
        total_pages = (total_players + per_page - 1) // per_page

    return render_template(
        "players.html",
        players=players,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        search_query=search_query
    )



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

@views.route("/add_team", methods=["GET", "POST"])
@admin_required
def add_team():
    if request.method == "POST":
        # Get the form values for the new player
        team_name = request.form.get("Team")
        abbreviations = request.form.get("Abbreviations")


        is_valid, error_message = validate_team_data(
            team_name, abbreviations
        )

        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("views.add_team"))

        query_max_id = text("SELECT MAX(Player_ID) FROM Players")
        max_player_id = db.session.execute(query_max_id).scalar()
        new_player_id = max_player_id + 1 if max_player_id else 1

        query_insert = text("""
                INSERT INTO Teams (team_name, team_abbreviation)
                VALUES (:team_name, :abbreviations)
            """)

        db.session.execute(
            query_insert,
            {
                "team_name": team_name,
                "abbreviations": abbreviations
            },
        )
        db.session.commit()

        flash("Team added successfully!", "success")
        return redirect(url_for("views.teams"))

    return render_template("add_team.html")


@views.route("/delete_team/<int:team_id>", methods=["POST"])
@admin_required
def delete_team(team_id):
    # Execute the DELETE SQL query directly
    query = text("DELETE FROM Teams WHERE team_id = :team_id")
    db.session.execute(query, {"team_id": team_id})

    db.session.commit()

    return redirect(url_for("views.teams"))


@views.route("/edit_team/<int:team_id>", methods=["GET", "POST"])
@admin_required
def edit_team(team_id):
    # Retrieve the player's details
    query = text("SELECT * FROM Teams WHERE team_id = :team_id")
    team = db.session.execute(query, {"team_id": team_id}).fetchone()

    if request.method == "POST":
        # Get updated values from the form
        team_name = request.form.get("Team")
        abbreviations = request.form.get("Abbreviations")


        is_valid, error_message = validate_team_data(
            team_name, abbreviations
        )

        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("views.edit_team", team_id=team_id))

        # Update the player's details in the database
        query_update = text("""
            UPDATE Teams
            SET team_name = :team_name,
                team_abbreviation = :abbreviations
            WHERE team_id = :team_id
        """)

        db.session.execute(
            query_update,
            {
                "team_id": team_id,
                "team_name": team_name,
                "abbreviations": abbreviations,
            },
        )
        db.session.commit()

        return redirect(url_for("views.teams"))

    return render_template("edit_team.html", team=team)

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
                    Seasons.season_id as season_id,
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

@views.route("/add_team_season_info", methods=["GET", "POST"])
def add_team_season_info():
    """
    View to add a new season record to the Team_Season_Info table.
    """

    # Optionally, fetch a list of teams and/or seasons to populate dropdowns in the form:
    teams = db.session.execute(text("SELECT team_id, team_name FROM Teams")).fetchall()
    seasons = db.session.execute(text("SELECT season_id, year FROM Seasons")).fetchall()

    if request.method == "POST":
        # Retrieve form fields
        team_id = request.form.get("team_id")         # e.g. from a <select> or hidden input
        season_id = request.form.get("season_id")     # e.g. from a <select>
        league = request.form.get("league", "")
        abbreviation = request.form.get("abbreviation", "")
        wins = request.form.get("wins", 0)
        losses = request.form.get("losses", 0)
        playoff_wins = request.form.get("playoff_wins", 0)
        playoff_losses = request.form.get("playoff_losses", 0)
        age = request.form.get("age", None)  # or some default

        # Perform the INSERT
        insert_query = text("""
            INSERT INTO Team_Season_Info (
                team_id, 
                season_id, 
                league, 
                abbreviation, 
                w, 
                l, 
                pw, 
                pl, 
                age
            ) VALUES (
                :team_id, 
                :season_id, 
                :league, 
                :abbreviation, 
                :wins, 
                :losses, 
                :playoff_wins, 
                :playoff_losses, 
                :age
            )
        """)

        try:
            db.session.execute(insert_query, {
                "team_id": team_id,
                "season_id": season_id,
                "league": league,
                "abbreviation": abbreviation,
                "wins": wins,
                "losses": losses,
                "playoff_wins": playoff_wins,
                "playoff_losses": playoff_losses,
                "age": age
            })
            db.session.commit()

            flash("New Team Season Info added successfully!", "success")
            return redirect(url_for("views.team_season_info"))

        except Exception as e:
            # Optional: log or print the error
            flash(f"Error while adding Team Season Info: {str(e)}", "error")
            db.session.rollback()

    # If GET or if there was an error, render the form again
    return render_template(
        "add_team_season_info.html",
        teams=teams,
        seasons=seasons
    )



@views.route("/delete_team_season_info/<int:team_id>/<int:season_id>", methods=["POST"])
@admin_required
def delete_team_season_info(team_id, season_id):
    # Execute the DELETE SQL query directly
    query = text("DELETE FROM Team_Season_Info WHERE team_id = :team_id AND season_id = :season_id")
    db.session.execute(query, {"team_id": team_id, "season_id": season_id})

    db.session.commit()

    return redirect(url_for("views.team_season_info"))


@views.route("/edit_team_season_info/<int:team_id>/<int:season_id>", methods=["GET", "POST"])
def edit_team_season_info(team_id, season_id):
    """
    View to edit a specific team's season record in the Team_Season_Info table.
    """

    # Fetch the existing record (if any)
    select_query = text("""
        SELECT TSI.team_id,
               TSI.season_id,
               league,
               abbreviation,
               w as wins,
               l as losses,
               pw as playoff_wins,
               pl as playoff_losses,
               age
        FROM Team_Season_Info AS TSI
        WHERE TSI.team_id = :team_id
          AND TSI.season_id = :season_id
    """)
    record = db.session.execute(
        select_query, 
        {"team_id": team_id, "season_id": season_id}
    ).fetchone()

    if not record:
        flash("No season info found for the specified team and season.", "error")
        return redirect(url_for("views.team_season_info"))

    if request.method == "POST":
        # Get updated field values from the form
        league = request.form.get("league", record.league)
        abbreviation = request.form.get("abbreviation", record.abbreviation)
        wins = request.form.get("wins", record.wins)
        losses = request.form.get("losses", record.losses)
        playoff_wins = request.form.get("playoff_wins", record.playoff_wins)
        playoff_losses = request.form.get("playoff_losses", record.playoff_losses)
        age = request.form.get("age", record.age)

        # Perform the update
        update_query = text("""
            UPDATE Team_Season_Info
            SET
                league = :league,
                abbreviation = :abbreviation,
                w = :wins,
                l = :losses,
                pw = :playoff_wins,
                pl = :playoff_losses,
                age = :age
            WHERE team_id = :team_id
              AND season_id = :season_id
        """)

        db.session.execute(update_query, {
            "league": league,
            "abbreviation": abbreviation,
            "wins": wins,
            "losses": losses,
            "playoff_wins": playoff_wins,
            "playoff_losses": playoff_losses,
            "age": age,
            "team_id": team_id,
            "season_id": season_id
        })

        db.session.commit()
        flash("Team season info updated successfully!", "success")

        # Redirect or render the same page, depending on your flow
        # Here we’ll redirect back to the main team_season_info page
        return redirect(url_for("views.team_season_info"))
    
    # If GET, render the edit form with existing values
    return render_template(
        "edit_team_season_info.html",
        record=record
    )


@views.route("/team_season_stats", methods=["GET", "POST"])
def team_season_stats():
    # Fetch all teams for the dropdown.
    all_teams = db.session.execute(text("SELECT * FROM Teams")).fetchall()

    selected_team = None
    results = []

    if request.method == "POST":
        selected_team = request.form.get("team")
        if selected_team:
            # Query the Team_Season_Stats table (join on Seasons to display year, if you wish).
            query = text("""
                SELECT
                  tss.team_id,
                  tss.season_id,
                  s.year as year,
                  tss.mov,
                  tss.sos,
                  tss.srs,
                  tss.o_rtg,
                  tss.d_rtg,
                  tss.n_rtg,
                  tss.pace,
                  tss.f_tr,
                  tss.x3p_ar,
                  tss.ts_percent,
                  tss.e_fg_percent,
                  tss.tov_percent,
                  tss.orb_percent,
                  tss.ft_fga,
                  tss.opp_e_fg_percent,
                  tss.opp_tov_percent,
                  tss.opp_drb_percent,
                  tss.opp_ft_fga,
                  tss.arena,
                  tss.attend,
                  tss.attend_g
                FROM Team_Season_Stats AS tss
                JOIN Seasons AS s ON tss.season_id = s.season_id
                WHERE tss.team_id = :team_id
            """)
            results = db.session.execute(query, {"team_id": selected_team}).fetchall()

    return render_template(
        "team_season_stats.html",
        teams=all_teams,
        results=results
    )


@views.route("/add_team_season_stats", methods=["GET", "POST"])
def add_team_season_stats():
    teams = db.session.execute(text("SELECT team_id, team_name FROM Teams")).fetchall()
    seasons = db.session.execute(text("SELECT season_id, year FROM Seasons")).fetchall()

    if request.method == "POST":
        # Get form fields
        team_id = request.form.get("team_id")
        season_id = request.form.get("season_id")

        # We'll parse everything else as float or strings as needed
        mov = request.form.get("mov", 0.0)
        sos = request.form.get("sos", 0.0)
        srs = request.form.get("srs", 0.0)
        o_rtg = request.form.get("o_rtg", 0.0)
        d_rtg = request.form.get("d_rtg", 0.0)
        n_rtg = request.form.get("n_rtg", 0.0)
        pace = request.form.get("pace", 0.0)
        f_tr = request.form.get("f_tr", 0.0)
        x3p_ar = request.form.get("x3p_ar", 0.0)
        ts_percent = request.form.get("ts_percent", 0.0)
        e_fg_percent = request.form.get("e_fg_percent", 0.0)
        tov_percent = request.form.get("tov_percent", 0.0)
        orb_percent = request.form.get("orb_percent", 0.0)
        ft_fga = request.form.get("ft_fga", 0.0)
        opp_e_fg_percent = request.form.get("opp_e_fg_percent", 0.0)
        opp_tov_percent = request.form.get("opp_tov_percent", 0.0)
        opp_drb_percent = request.form.get("opp_drb_percent", 0.0)
        opp_ft_fga = request.form.get("opp_ft_fga", 0.0)
        arena = request.form.get("arena", "")
        attend = request.form.get("attend", 0)
        attend_g = request.form.get("attend_g", 0)

        insert_query = text("""
            INSERT INTO Team_Season_Stats (
                team_id, season_id, 
                mov, sos, srs, o_rtg, d_rtg, n_rtg, pace, f_tr, x3p_ar, 
                ts_percent, e_fg_percent, tov_percent, orb_percent, ft_fga, 
                opp_e_fg_percent, opp_tov_percent, opp_drb_percent, opp_ft_fga,
                arena, attend, attend_g
            )
            VALUES (
                :team_id, :season_id,
                :mov, :sos, :srs, :o_rtg, :d_rtg, :n_rtg, :pace, :f_tr, :x3p_ar,
                :ts_percent, :e_fg_percent, :tov_percent, :orb_percent, :ft_fga,
                :opp_e_fg_percent, :opp_tov_percent, :opp_drb_percent, :opp_ft_fga,
                :arena, :attend, :attend_g
            )
        """)

        try:
            db.session.execute(insert_query, {
                "team_id": team_id,
                "season_id": season_id,
                "mov": mov,
                "sos": sos,
                "srs": srs,
                "o_rtg": o_rtg,
                "d_rtg": d_rtg,
                "n_rtg": n_rtg,
                "pace": pace,
                "f_tr": f_tr,
                "x3p_ar": x3p_ar,
                "ts_percent": ts_percent,
                "e_fg_percent": e_fg_percent,
                "tov_percent": tov_percent,
                "orb_percent": orb_percent,
                "ft_fga": ft_fga,
                "opp_e_fg_percent": opp_e_fg_percent,
                "opp_tov_percent": opp_tov_percent,
                "opp_drb_percent": opp_drb_percent,
                "opp_ft_fga": opp_ft_fga,
                "arena": arena,
                "attend": attend,
                "attend_g": attend_g
            })
            db.session.commit()

            flash("Team season stats added successfully!", "success")
            return redirect(url_for("views.team_season_stats"))

        except Exception as e:
            flash(f"Error adding team season stats: {str(e)}", "error")
            db.session.rollback()

    return render_template("add_team_season_stats.html", teams=teams, seasons=seasons)


@views.route("/edit_team_season_stats/<int:team_id>/<int:season_id>", methods=["GET", "POST"])
def edit_team_season_stats(team_id, season_id):
    # Fetch the existing record
    select_query = text("""
        SELECT
            team_id,
            season_id,
            mov,
            sos,
            srs,
            o_rtg,
            d_rtg,
            n_rtg,
            pace,
            f_tr,
            x3p_ar,
            ts_percent,
            e_fg_percent,
            tov_percent,
            orb_percent,
            ft_fga,
            opp_e_fg_percent,
            opp_tov_percent,
            opp_drb_percent,
            opp_ft_fga,
            arena,
            attend,
            attend_g
        FROM Team_Season_Stats
        WHERE team_id = :team_id
          AND season_id = :season_id
    """)
    record = db.session.execute(select_query, {
        "team_id": team_id,
        "season_id": season_id
    }).fetchone()

    if not record:
        flash("No team season stats found for the specified team and season.", "error")
        return redirect(url_for("views.team_season_stats"))

    if request.method == "POST":
        # Gather updated fields from the form (default to existing record values if not provided)
        mov = request.form.get("mov", record.mov)
        sos = request.form.get("sos", record.sos)
        srs = request.form.get("srs", record.srs)
        o_rtg = request.form.get("o_rtg", record.o_rtg)
        d_rtg = request.form.get("d_rtg", record.d_rtg)
        n_rtg = request.form.get("n_rtg", record.n_rtg)
        pace = request.form.get("pace", record.pace)
        f_tr = request.form.get("f_tr", record.f_tr)
        x3p_ar = request.form.get("x3p_ar", record.x3p_ar)
        ts_percent = request.form.get("ts_percent", record.ts_percent)
        e_fg_percent = request.form.get("e_fg_percent", record.e_fg_percent)
        tov_percent = request.form.get("tov_percent", record.tov_percent)
        orb_percent = request.form.get("orb_percent", record.orb_percent)
        ft_fga = request.form.get("ft_fga", record.ft_fga)
        opp_e_fg_percent = request.form.get("opp_e_fg_percent", record.opp_e_fg_percent)
        opp_tov_percent = request.form.get("opp_tov_percent", record.opp_tov_percent)
        opp_drb_percent = request.form.get("opp_drb_percent", record.opp_drb_percent)
        opp_ft_fga = request.form.get("opp_ft_fga", record.opp_ft_fga)
        arena = request.form.get("arena", record.arena)
        attend = request.form.get("attend", record.attend)
        attend_g = request.form.get("attend_g", record.attend_g)

        update_query = text("""
            UPDATE Team_Season_Stats
            SET
                mov = :mov,
                sos = :sos,
                srs = :srs,
                o_rtg = :o_rtg,
                d_rtg = :d_rtg,
                n_rtg = :n_rtg,
                pace = :pace,
                f_tr = :f_tr,
                x3p_ar = :x3p_ar,
                ts_percent = :ts_percent,
                e_fg_percent = :e_fg_percent,
                tov_percent = :tov_percent,
                orb_percent = :orb_percent,
                ft_fga = :ft_fga,
                opp_e_fg_percent = :opp_e_fg_percent,
                opp_tov_percent = :opp_tov_percent,
                opp_drb_percent = :opp_drb_percent,
                opp_ft_fga = :opp_ft_fga,
                arena = :arena,
                attend = :attend,
                attend_g = :attend_g
            WHERE team_id = :team_id
              AND season_id = :season_id
        """)
        try:
            db.session.execute(update_query, {
                "mov": mov,
                "sos": sos,
                "srs": srs,
                "o_rtg": o_rtg,
                "d_rtg": d_rtg,
                "n_rtg": n_rtg,
                "pace": pace,
                "f_tr": f_tr,
                "x3p_ar": x3p_ar,
                "ts_percent": ts_percent,
                "e_fg_percent": e_fg_percent,
                "tov_percent": tov_percent,
                "orb_percent": orb_percent,
                "ft_fga": ft_fga,
                "opp_e_fg_percent": opp_e_fg_percent,
                "opp_tov_percent": opp_tov_percent,
                "opp_drb_percent": opp_drb_percent,
                "opp_ft_fga": opp_ft_fga,
                "arena": arena,
                "attend": attend,
                "attend_g": attend_g,
                "team_id": team_id,
                "season_id": season_id
            })
            db.session.commit()
            flash("Team season stats updated successfully!", "success")
            return redirect(url_for("views.team_season_stats"))
        except Exception as e:
            flash(f"Error updating team season stats: {str(e)}", "error")
            db.session.rollback()

    return render_template("edit_team_season_stats.html", record=record)


@views.route("/delete_team_season_stats/<int:team_id>/<int:season_id>", methods=["POST"])
def delete_team_season_stats(team_id, season_id):
    delete_query = text("""
        DELETE FROM Team_Season_Stats
        WHERE team_id = :team_id
          AND season_id = :season_id
    """)
    try:
        db.session.execute(delete_query, {"team_id": team_id, "season_id": season_id})
        db.session.commit()
        flash("Team season stats deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting team season stats: {str(e)}", "error")
        db.session.rollback()

    return redirect(url_for("views.team_season_stats"))


@views.route("/teams_dashboard", methods=["GET", "POST"])
def teams_dashboard():
    """
    Renders a functional NBA Teams Dashboard using Tailwind CSS and Chart.js.
    Allows optional filtering by team and season range.
    """

    # === 1) Fetch all teams for the dropdown
    # Adjust this query to match your Teams table.
    teams_query = text("""SELECT team_id, team_name FROM Teams ORDER BY team_name""")
    all_teams = db.session.execute(teams_query).fetchall()

    # === 2) Parse form inputs 
    if request.method == "POST":
        selected_team_id = request.form.get("team_id")
        season_start = request.form.get("season_start")
        season_end = request.form.get("season_end")
    else:
        selected_team_id = all_teams[2].team_id if all_teams else None
        season_start = None
        season_end = None

    # === 3) Query for key metrics 
    base_key_metrics_query = """
        SELECT
            tsi.w AS wins,
            tsi.l AS losses,
            CASE WHEN tsi.playoffs = 1 THEN "Playoffs" ELSE "No Playoffs" END AS playoff_status,
            tss.o_rtg AS offensive_rating,
            tss.d_rtg AS defensive_rating,
            s.year,
            tss.arena
        FROM Team_Season_Info tsi
        JOIN Team_Season_Stats tss ON (tsi.team_id = tss.team_id AND tsi.season_id = tss.season_id)
        JOIN Seasons s ON (tsi.season_id = s.season_id)
        WHERE tsi.team_id = :team_id
    """

    params = {"team_id": selected_team_id}

    # If user provided a season range, apply it
    if season_start and season_end:
        base_key_metrics_query += " AND s.year BETWEEN :start AND :end"
        params["start"] = int(season_start)
        params["end"] = int(season_end)

    # We’ll just grab the latest season from the filtered set
    base_key_metrics_query += """
        ORDER BY s.year DESC
        LIMIT 1
    """

    key_metrics_query = text(base_key_metrics_query)
    key_metrics = db.session.execute(key_metrics_query, params).fetchone()

    # === 4) Advanced stats
    if key_metrics:
        year_for_adv = key_metrics.year
    else:
        year_for_adv = 2023  # default fallback

    adv_query = text("""
        SELECT
            t.team_name AS team,
            tss.srs,
            tss.mov,
            CONCAT(ROUND(tss.e_fg_percent * 100,1), '%') AS efg_percent,
            tss.pace,
            tss.o_rtg AS ortg,
            tss.d_rtg AS drtg
        FROM Team_Season_Stats tss
        JOIN Teams t ON t.team_id = tss.team_id
        JOIN Seasons s ON s.season_id = tss.season_id
        WHERE s.year = :year
        ORDER BY tss.srs DESC
        LIMIT 10
    """)
    advanced_stats = db.session.execute(adv_query, {"year": year_for_adv}).fetchall()

    # === 5) Team Roster query
    roster_query = text("""
        SELECT
            p.Player AS player_name,
            pips.Position AS position,
            CASE WHEN p.HOF = 1 THEN 'Hall of Fame' ELSE 'Active' END AS status,
            ROUND(pss.PER, 1) AS per,
            ROUND(pss.TS_Percent * 100, 1) AS ts_pct
        FROM Players p
        JOIN Player_Info_Per_Season pips ON pips.Player_ID = p.Player_ID
        LEFT JOIN Player_Season_Stats pss ON (pss.Player_ID = pips.Player_ID AND pss.Season_ID = pips.Season_ID)
        WHERE pips.Team_ID = :team_id
          AND pips.Season_ID IN (
              SELECT season_id FROM Seasons WHERE year = :year
          )
        ORDER BY p.Player
    """)
    roster = db.session.execute(
        roster_query, {"team_id": selected_team_id, "year": year_for_adv}
    ).fetchall()

    # === 6) Data for a line chart (e.g., eFG% over multiple seasons) ===
    chart_data_query = text("""
        SELECT 
            s.year,
            ROUND(tss.e_fg_percent * 100, 1) as efg
        FROM Team_Season_Stats tss
        JOIN Seasons s ON s.season_id = tss.season_id
        WHERE tss.team_id = :team_id
        ORDER BY s.year
    """)
    chart_data_rows = db.session.execute(chart_data_query, {"team_id": selected_team_id}).fetchall()

    # We'll turn this into lists for Chart.js
    years_list = [row.year for row in chart_data_rows]
    efg_list = [float(row.efg) for row in chart_data_rows]

    return render_template(
        "teams_dashboard.html",
        teams=all_teams,
        selected_team_id=selected_team_id,
        season_start=season_start,
        season_end=season_end,
        key_metrics=key_metrics,
        advanced_stats=advanced_stats,
        roster=roster,
        chart_years=years_list,
        chart_efg=efg_list,
    )

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
