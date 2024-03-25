from dotenv import dotenv_values

import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    lang TEXT DEFAULT 'ru',
    idk TEXT DEFAULT 'static'
)
""")


config = dotenv_values(".env")


def get_from_config(query):
    """Get variable from .env config"""
    try:
        result = config[query]
    except:
        result = "not found"
    return result


def user_in_db(user_id):
    cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    res = cursor.fetchone()

    if res is None:
        return False 
    return res[0]


def add_user(user_id, name):
    cursor.execute("INSERT INTO users (id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.commit()
    return


def edit_user(user_id, name):
    cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
    conn.commit()
    conn.commit()
    return


