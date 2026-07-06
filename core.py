# Copyright (C) 2026 Murilo Gomes Julio
# SPDX-License-Identifier: GPL-2.0-only

# Site: https://github.com/bluiceoficial

import sqlite3, os
from cryptography.fernet import Fernet
from totp import generate_totp

BASE_DIR = os.path.expanduser("~/.config/migetauth")
DB_NAME = os.path.join(BASE_DIR, "auth.db")
KEY_FILE = os.path.join(BASE_DIR, "secret.key")

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Criptografia
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

fernet = Fernet(load_key())

def encrypt(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt(text):
    return fernet.decrypt(text.encode()).decode()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            secret TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_account(name, secret):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    enc_secret = encrypt(secret)

    cursor.execute("INSERT INTO accounts (name, secret) VALUES (?, ?)",
                   (name, enc_secret))
    conn.commit()
    conn.close()

def get_accounts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, secret FROM accounts")
    rows = cursor.fetchall()

    conn.close()
    return rows

#TOTP
def generate_token(secret):
    return generate_totp(secret)

def update_account(acc_id, new_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET name = ? WHERE id = ?", (new_name, acc_id))
    conn.commit()
    conn.close()

def delete_account_db(acc_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE id = ?", (acc_id,))
    conn.commit()
    conn.close()
