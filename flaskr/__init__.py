import os

from flask import Flask, redirect, render_template, request, session
from markupsafe import escape

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import db_connect


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route("/")
    def index():
        return redirect("/login")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if session.get("username", -1) != -1:
            return redirect("/game")

        if request.method == "POST":
            username_input = escape(request.form.get("username", None)).strip().lower()
            password_input = escape(request.form.get("password", None))

            if username_input is None or password_input is None:
                return render_template("auth/login.html", login_error="Username and/or password are empty")

            row = None
            connection = db_connect()

            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE username = %s", (username_input,))
                    row = cursor.fetchone()

            connection.close()

            if row is None or check_password_hash(row[2], password_input):
                return render_template("auth/login.html", login_error="Invalid credentials")
            else:
                session["username"] = row[1]
                return redirect("/game")

        else:
            return render_template("auth/login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if session.get("username", -1) != -1:
            return redirect("/game")

        if request.method == "POST":
            username_input = escape(request.form.get("username", None)).strip().lower()
            password_input = escape(request.form.get("password", None))
            confirm_password_input = escape(request.form.get("confirm_password", None))

            if username_input is None or password_input is None or confirm_password_input is None:
                return render_template("auth/register.html",
                                       register_error="Username and/or password and/or confirm password are empty")
            elif password_input != confirm_password_input:
                return render_template("auth/register.html", register_error="Passwords do not match")

            row = None
            connection = db_connect()

            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE username = %s", (username_input,))
                    row = cursor.fetchone()

            connection.close()

            if row is not None:
                return render_template("auth/register.html", register_error="Username already used")
            else:
                connection = db_connect()

                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO users (username,password) VALUES (%s,%s)",
                                       (username_input, generate_password_hash(password_input)), )

                connection.close()

                session["username"] = username_input

                return redirect("/game")
        else:
            return render_template("auth/register.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

    @app.route("/game")
    def game():
        return render_template("game.html", username=session.get("username"))

    return app
