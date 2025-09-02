# app/routes/landing.py

from flask import Blueprint, render_template

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    """Display landing page"""
    return render_template('landing.html')

@landing_bp.route('/home')
def home():
    """Alternative route for landing page"""
    return render_template('landing.html')

@landing_bp.route('/about')
def about():
    """About page"""
    return render_template('landing.html')  # You can create a separate about.html later
