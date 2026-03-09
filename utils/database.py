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
            # Table for user tracking and limits
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    count INTEGER DEFAULT 0,
                    last_date TEXT,
                    extra_limit INTEGER DEFAULT 0,
                    referred_by INTEGER,
                    total_referrals INTEGER DEFAULT 0
                )
            """)

    def check_user(self, user_id, daily_limit):
        today = str(date.today())
        with self.conn:
            cursor = self.conn.execute("SELECT count, last_date, extra_limit FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if not row:
                self.conn.execute("INSERT INTO users (user_id, count, last_date) VALUES (?, 1, ?)", (user_id, today))
                return True, 1, daily_limit
            
            count, last_date, extra_limit = row
            current_total_limit = daily_limit + extra_limit

            if last_date != today:
                self.conn.execute("UPDATE users SET count = 1, last_date = ? WHERE user_id = ?", (today, user_id))
                return True, 1, current_total_limit
            
            if count >= current_total_limit:
                return False, count, current_total_limit
            
            new_count = count + 1
            self.conn.execute("UPDATE users SET count = ? WHERE user_id = ?", (new_count, user_id))
            return True, new_count, current_total_limit

    def add_referral(self, new_user_id, referrer_id):
        with self.conn:
            # Check if user already exists
            cursor = self.conn.execute("SELECT user_id FROM users WHERE user_id = ?", (new_user_id,))
            if cursor.fetchone():
                return False # Old user
            
            # Create new user
            self.conn.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (new_user_id, referrer_id))
            # Update referrer: +1 referral and +20 bonus limit
            self.conn.execute("UPDATE users SET extra_limit = extra_limit + 10, total_referrals = total_referrals + 1 WHERE user_id = ?", (referrer_id,))
            return True

    def get_user_data(self, user_id):
        with self.conn:
            cursor = self.conn.execute("SELECT extra_limit, total_referrals FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

    def get_total_users(self):
        with self.conn:
            cursor = self.conn.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

db = Database()
