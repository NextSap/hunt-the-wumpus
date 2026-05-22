#! /usr/bin/env python3

# DI ILIO LOUIS py02

import re

from flask import Flask, redirect, render_template, request, session
from markupsafe import escape

from werkzeug.security import check_password_hash, generate_password_hash

from db import db_connect
from game import create_map, is_map_playable, place_pits, place_wumpus, place_bats, place_player, \
    move_player, shoot_arrow

app = Flask(__name__)
app.config.from_pyfile("config.py")


@app.route("/")
def index():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username", -1) != -1:
        return redirect("/menu")

    if request.method == "POST":
        username_input = escape(request.form.get("username", None)).strip().lower()
        password_input = escape(request.form.get("password", None))

        if username_input is None or password_input is None:
            return render_template("auth/login.html", login_error="Username and/or password are empty")

        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username_input,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()

        if row is None or not check_password_hash(row[2], password_input):
            return render_template("auth/login.html", login_error="Invalid credentials")
        else:
            session["username"] = row[1]
            session["game_state"] = "MENU1"

            return redirect("/menu")
    else:
        return render_template("auth/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("username", -1) != -1:
        return redirect("/game")

    if request.method == "POST":
        username_input = escape(request.form.get("username", None)).strip().lower()
        username_exp = '^[a-zA-Z0-9]+$'
        password_input = escape(request.form.get("password", None))
        password_exp = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,50}$'
        confirm_password_input = escape(request.form.get("confirm_password", None))

        if username_input is None or password_input is None or confirm_password_input is None:
            return render_template("auth/register.html",
                                   register_error="Username and/or password and/or confirm password are empty")
        elif password_input != confirm_password_input:
            return render_template("auth/register.html", register_error="Passwords do not match")

        elif not re.match(password_exp, password_input) or not re.match(username_exp, username_input):
            return render_template("auth/register.html", register_error="Username and/or Password does not match requirements")

        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username_input,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()

        if row is not None:
            return render_template("auth/register.html", register_error="Username already used")
        else:
            connection = db_connect()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username,password) VALUES (%s,%s)",
                           (username_input, generate_password_hash(password_input)), )
            connection.commit()
            cursor.close()
            connection.close()

            session["username"] = username_input

            return redirect("/menu")
    else:
        return render_template("auth/register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/game")
def game():
    if session.get("username", -1) == -1:
        return redirect("/login")

    game_state = session.get("game_state")

    if game_state not in ("PLAYING", "VICTORY", "DEFEAT"):
        return redirect("/menu")

    game_map = session.get("game_map", [])
    difficulty = session["difficulty"]

    if not game_map:
        session["unavailable_locations"] = []
        session["game_map_visibility"] = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        is_playable = False
        while not is_playable:
            game_map = create_map(difficulty)
            is_playable = is_map_playable(game_map)

        place_pits(game_map)
        place_wumpus(game_map)
        place_bats(game_map, 1 if difficulty == 1 else 2)
        place_player(game_map)
        session["game_map"] = game_map

    return render_template("game.html")


@app.route("/move/<direction>")
def move(direction):
    if session.get("username", -1) == -1:
        return redirect("/login")

    if session.get("game_state") in ("VICTORY", "DEFEAT"):
        return redirect("/game")

    if session.get("game_state") != "PLAYING":
        return redirect("/menu")

    direction = direction.upper()

    if direction in ["LEFT", "RIGHT", "UP", "DOWN"]:
        move_player(direction)

    return redirect("/game")


@app.route("/menu")
def menu():
    if session.get("username", -1) == -1:
        return redirect("/login")

    if session.get("game_state") in ("PLAYING", "VICTORY", "DEFEAT"):
        return redirect("/game")

    game_state = session.get("game_state", "MENU1")

    menu_steps = {
        "MENU1": ["NEW_GAME", "RANKING", "LOG_OUT"],
        "MENU2": ["BACK", "EASY", "MEDIUM", 'HARD'],
        "MENU3": ["BACK", "EXPRESS", "BLINDFOLD", "START_PLAYING"],
    }

    return render_template("menu.html", options=menu_steps.get(game_state))


@app.route("/menu-handler", methods=["POST"])
def menu_handler():
    choice = request.form.get("choice")

    if choice == "NEW_GAME":
        session["game_state"] = "MENU2"

    elif choice == "RANKING":
        return redirect("/ranking")

    elif choice == "LOG_OUT":
        return redirect("/logout")

    elif choice in ["EASY", "MEDIUM", "HARD"]:
        session["difficulty"] = 1 if choice == "EASY" else 2 if choice == "MEDIUM" else 3
        session["game_state"] = "MENU3"

    elif choice == "BACK":
        current_state = session.get("game_state", "MENU1")
        session["game_state"] = f"MENU{int(current_state[-1]) - 1}"

    elif choice == "TOGGLE_EXPRESS":
        session["express"] = not session.get("express", False)

    elif choice == "TOGGLE_BLINDFOLD":
        session["blindfold"] = not session.get("blindfold", False)

    elif choice == "START_PLAYING":
        session["game_state"] = "PLAYING"
        return redirect("/game")

    return redirect("/menu")


@app.route("/ranking")
def ranking():
    if session.get("username", -1) == -1:
        return redirect("/login")

    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT username, victory, defeat_wumpus, defeat_pit, defeat_arrow FROM users ORDER BY -victory,defeat_wumpus,defeat_pit,defeat_arrow LIMIT 10")
    row = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("ranking.html", ranking=row)


@app.route("/debug")
def debug():
    return render_template("debug.html")


@app.route("/arrow/<direction>")
def arrow(direction):
    if session.get("username", -1) == -1:
        return redirect("/login")

    if session.get("game_state") in ("VICTORY", "DEFEAT"):
        return redirect("/game")

    if session.get("game_state") != "PLAYING":
        return redirect("/menu")

    direction = direction.upper()

    if direction in ["LEFT", "RIGHT", "UP", "DOWN"]:
        shoot_arrow(direction)

    return redirect("/game")


@app.route("/back-menu")
def back_menu():
    if session.get("username", -1) == -1:
        return redirect("/login")

    username = session.get("username")
    session.clear()
    session["game_state"] = "MENU1"
    session["username"] = username

    return redirect("/menu")
