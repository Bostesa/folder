# utils.py
from functools import wraps
from flask import session, flash, redirect, url_for
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="my-secret-pw",
        database="CarCompanyDB",
        port=3306
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to view this page.", "error")
            return redirect(url_for('auth.login')) 
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("You need to be logged in to view this page.", "error")
                return redirect(url_for('auth.login'))

            role_name = session.get('role_name')
            if role_name != 'Administrator' and role_name not in allowed_roles:
                flash("You do not have access to that page.", "error")
                return redirect(url_for('dashboard.dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def fetch_all(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def fetch_one(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def execute_commit(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()