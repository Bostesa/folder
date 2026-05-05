# dashboard.py
from flask import Blueprint, render_template, session, flash
import mysql.connector
from utils import get_db_connection, login_required

# Define the blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user_id=session['user_id'])
