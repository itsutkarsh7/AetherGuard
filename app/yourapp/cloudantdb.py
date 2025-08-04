# app/dashboard.py

from flask import Blueprint, render_template, session, redirect, url_for
from cloudant.client import Cloudant
import os

# Define the dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Connect to IBM Cloudant
client = Cloudant.iam(
    os.getenv("CLOUDANT_USERNAME"),
    os.getenv("CLOUDANT_API_KEY"),
    connect=True
)

# Access the SentinelAI database
db = client[os.getenv("CLOUDANT_DB_NAME")]

@dashboard_bp.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    # Fetch counts from Cloudant
    user_count = len([doc for doc in db if doc.get('type') == 'user'])
    threat_count = len([doc for doc in db if doc.get('type') == 'threat'])
    alert_count = len([doc for doc in db if doc.get('type') == 'alert'])  # New: alert type
    log_count = len([doc for doc in db if doc.get('type') == 'log'])

    return render_template(
        'dashboard.html',
        user=session['user'],
        user_count=user_count,
        threat_count=threat_count,
        alert_count=alert_count,
        log_count=log_count
    )
