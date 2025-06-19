import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 🔗 DB কানেকশন ফাংশন
def get_connection():
    return psycopg2.connect(DATABASE_URL)

# 🔹 Database টেবিল তৈরি
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            token TEXT,
            confirmed BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# 🔹 নতুন ইউজার ইনসার্ট
def insert_user(email, token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (email, token) VALUES (%s, %s)', (email, token))
    conn.commit()
    cursor.close()
    conn.close()

# 🔹 ইমেইল দিয়ে ইউজার খোঁজা
def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# 🔹 টোকেন দিয়ে ইউজার খোঁজা
def get_user_by_token(token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE token = %s', (token,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# 🔹 ইউজার কনফার্ম (confirmed = True)
def confirm_user(token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET confirmed = TRUE WHERE token = %s', (token,))
    conn.commit()
    cursor.close()
    conn.close()
