import sqlite3
from datetime import date
import os

class Database:
    def __init__(self):
        # This will create a local file named bot_db.sqlite
        self.conn = sqlite3.connect("bot_db.sqlite", check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    count INTEGER DEFAULT 0,
                    last_date TEXT
                )
            """)

    def check_user(self, user_id, daily_limit):
        today = str(date.today())
        with self.conn:
            cursor = self.conn.execute("SELECT count, last_date FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if not row:
                self.conn.execute("INSERT INTO users (user_id, count, last_date) VALUES (?, 1, ?)", (user_id, today))
                return True, 1
            
            count, last_date = row
            if last_date != today:
                self.conn.execute("UPDATE users SET count = 1, last_date = ? WHERE user_id = ?", (today, user_id))
                return True, 1
            
            if count >= daily_limit:
                return False, count
            
            new_count = count + 1
            self.conn.execute("UPDATE users SET count = ? WHERE user_id = ?", (new_count, user_id))
            return True, new_count

    def get_total_users(self):
        with self.conn:
            cursor = self.conn.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

db = Database()
