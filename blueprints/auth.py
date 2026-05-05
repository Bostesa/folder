# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from utils import get_db_connection

# Define the blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.user_id, u.username, u.password, u.role_id, r.role_name
            FROM `User` u
            JOIN Role r ON u.role_id = r.role_id
            WHERE u.username = %s AND u.active = TRUE
            """,
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role_id'] = user['role_id']
            session['role_name'] = user['role_name']
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "error")
            return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been successfully logged out.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    flash("Administrators create accounts from the Admin Users page.", "error")
    if 'user_id' in session:
        return redirect(url_for('directory.admin_users'))
    return redirect(url_for('auth.login'))