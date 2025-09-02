# app/routes/dashboard.py

from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app
from functools import wraps
from bson import ObjectId

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Display main dashboard"""
    user = current_app.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('dashboard.html', user=user)

@dashboard_bp.route('/dashboard/threats')
@login_required
def threats():
    """Display threat analysis page"""
    return render_template('threats.html')

@dashboard_bp.route('/dashboard/settings')
@login_required
def settings():
    """Display user settings page"""
    user = current_app.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('settings.html', user=user)
