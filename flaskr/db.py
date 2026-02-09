import psycopg2
from flask import current_app, g


def db_connect():
    if 'db' not in g:
        g.db = psycopg2.connect(database=current_app.config.get("DB_NAME"),
                                user=current_app.config.get("DB_USER"),
                                password=current_app.config.get("DB_PASSWORD"),
                                host=current_app.config.get("DB_HOST"),
                                port=current_app.config.get("DB_PORT"))

    return g.db


def db_close():
    db = g.pop('db', None)

    if db is not None:
        db.close()