import sqlite3

DB_PATH = 'kamenozrut_server.db'

# TODO need to add DB tests
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS active_users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nickname TEXT NOT NULL UNIQUE,
        ip_address TEXT NOT NULL)
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS multiplayer_scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nickname1 TEXT NOT NULL,
        score1 INTEGER,
        nickname2 TEXT NOT NULL,
        score2 INTEGER,
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (nickname1) REFERENCES active_users(nickname),
        FOREIGN KEY (nickname2) REFERENCES active_users(nickname))
    """)
    conn.commit()
    conn.close()


def nickname_exists(nickname):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM active_users WHERE nickname = ?", (nickname,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def add_active_user(nickname, ip_address):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO active_users (nickname, ip_address) VALUES (?,?)", (nickname, ip_address))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def remove_active_user(nickname):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_users where nickname = ?", (nickname,))
    conn.commit()
    conn.close()
