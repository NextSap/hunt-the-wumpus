import os

from flask import Flask, redirect, render_template


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/')
    def index():
        return redirect("/login")

    @app.route('/login')
    def login():
        return render_template('auth/login.html')

    @app.route('/register')
    def register():
        return render_template('auth/register.html')

    return app