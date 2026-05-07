import psycopg2
from flask import current_app


def db_connect():
    return psycopg2.connect(database=current_app.config.get("DB_NAME"),
                            user=current_app.config.get("DB_USER"),
                            password=current_app.config.get("DB_PASSWORD"),
                            host=current_app.config.get("DB_HOST"),
                            port=current_app.config.get("DB_PORT"))


def add_wumpus_defeat(username):
    """Add a wumpus defeat to user in database"""

    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("SELECT defeat_wumpus FROM users WHERE username=%s", (username,))
    number_wumpus_defeat = cursor.fetchone()[0]
    cursor.execute("UPDATE users SET defeat_wumpus=%s WHERE username=%s", (number_wumpus_defeat+1,username,))
    connection.commit()
    cursor.close()
    connection.close()


def add_pit_defeat(username):
    """Add a pit defeat to user in database"""

    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("SELECT defeat_pit FROM users WHERE username=%s", (username,))
    number_pit_defeat = cursor.fetchone()[0]
    cursor.execute("UPDATE users SET defeat_pit=%s WHERE username=%s", (number_pit_defeat+1,username,))
    connection.commit()
    cursor.close()
    connection.close()


def add_arrow_defeat(username):
    """Add an arrow defeat to user in database"""

    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("SELECT defeat_arrow FROM users WHERE username=%s", (username,))
    number_arrow_defeat = cursor.fetchone()[0]
    cursor.execute("UPDATE users SET defeat_arrow=%s WHERE username=%s", (number_arrow_defeat+1,username,))
    connection.commit()
    cursor.close()
    connection.close()


def add_victory(username):
    """Add a victory to user in database"""

    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("SELECT victory FROM users WHERE username=%s", (username,))
    number_victory = cursor.fetchone()[0]
    cursor.execute("UPDATE users SET victory=%s WHERE username=%s", (number_victory + 1, username,))
    connection.commit()
    cursor.close()
    connection.close()