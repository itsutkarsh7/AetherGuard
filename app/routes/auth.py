# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from datetime import datetime
import secrets

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')

@auth_bp.route('/login')
def login():
    """Display login page"""
    return render_template('login.html')

@auth_bp.route('/register')
def register():
    """Display register page (same as login with different tab)"""
    return render_template('login.html', tab='register')

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('landing.home'))

# Manual Login/Register Routes
@auth_bp.route('/manual/login', methods=['POST'])
def manual_login():
    """Handle manual login with email/password"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Email and password are required.', 'error')
        return redirect(url_for('auth.login'))
    
    # Find user in database
    user = current_app.db.users.find_one({'email': email})
    
    if user and check_password_hash(user['password'], password):
        # Login successful
        session['user_id'] = str(user['_id'])
        session['user_email'] = user['email']
        session['user_name'] = user['name']
        session['user_avatar'] = user.get('avatar', '')
        flash(f'Welcome back, {user["name"]}!', 'success')
        return redirect(url_for('dashboard.dashboard'))
    else:
        flash('Invalid email or password.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/manual/register', methods=['POST'])
def manual_register():
    """Handle manual registration with email/password"""
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([name, email, password, confirm_password]):
        flash('All fields are required.', 'error')
        return redirect(url_for('auth.register'))
    
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('auth.register'))
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return redirect(url_for('auth.register'))
    
    # Check if user already exists
    if current_app.db.users.find_one({'email': email}):
        flash('An account with this email already exists.', 'error')
        return redirect(url_for('auth.register'))
    
    # Create new user
    user_data = {
        'name': name,
        'email': email,
        'password': generate_password_hash(password),
        'avatar': f"https://ui-avatars.com/api/?name={name}&background=0891b2&color=fff",
        'provider': 'manual',
        'created_at': datetime.utcnow(),
        'last_login': datetime.utcnow()
    }
    
    result = current_app.db.users.insert_one(user_data)
    
    # Auto-login after registration
    session['user_id'] = str(result.inserted_id)
    session['user_email'] = email
    session['user_name'] = name
    session['user_avatar'] = user_data['avatar']
    
    flash(f'Account created successfully! Welcome, {name}!', 'success')
    return redirect(url_for('dashboard.dashboard'))

# Google OAuth Routes
@auth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login"""
    if not GOOGLE_CLIENT_ID:
        flash('Google OAuth is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    # Generate state for security
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Build Google OAuth URL
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={request.url_root}auth/google/callback&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"state={state}"
    )
    
    return redirect(google_auth_url)

@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    # Verify state parameter
    if request.args.get('state') != session.get('oauth_state'):
        flash('Invalid state parameter. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    code = request.args.get('code')
    if not code:
        flash('Authorization failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    # Exchange code for token
    token_data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': f"{request.url_root}auth/google/callback"
    }
    
    token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
    
    if token_response.status_code != 200:
        flash('Failed to obtain access token from Google.', 'error')
        return redirect(url_for('auth.login'))
    
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    # Get user info from Google
    user_response = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if user_response.status_code != 200:
        flash('Failed to get user information from Google.', 'error')
        return redirect(url_for('auth.login'))
    
    user_info = user_response.json()
    
    # Find or create user
    user = current_app.db.users.find_one({'email': user_info['email']})
    
    if user:
        # Update existing user
        current_app.db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
    else:
        # Create new user
        user_data = {
            'name': user_info['name'],
            'email': user_info['email'],
            'avatar': user_info['picture'],
            'provider': 'google',
            'google_id': user_info['id'],
            'created_at': datetime.utcnow(),
            'last_login': datetime.utcnow()
        }
        result = current_app.db.users.insert_one(user_data)
        user = current_app.db.users.find_one({'_id': result.inserted_id})
    
    # Set session
    session['user_id'] = str(user['_id'])
    session['user_email'] = user['email']
    session['user_name'] = user['name']
    session['user_avatar'] = user['avatar']
    
    flash(f'Successfully logged in with Google! Welcome, {user["name"]}!', 'success')
    return redirect(url_for('dashboard.dashboard'))

# GitHub OAuth Routes
@auth_bp.route('/github')
def github_login():
    """Initiate GitHub OAuth login"""
    if not GITHUB_CLIENT_ID:
        flash('GitHub OAuth is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    # Generate state for security
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Build GitHub OAuth URL
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={request.url_root}auth/github/callback&"
        f"scope=user:email&"
        f"state={state}"
    )
    
    return redirect(github_auth_url)

@auth_bp.route('/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    # Verify state parameter
    if request.args.get('state') != session.get('oauth_state'):
        flash('Invalid state parameter. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    code = request.args.get('code')
    if not code:
        flash('Authorization failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    # Exchange code for token
    token_data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    
    headers = {'Accept': 'application/json'}
    token_response = requests.post('https://github.com/login/oauth/access_token', 
                                 data=token_data, headers=headers)
    
    if token_response.status_code != 200:
        flash('Failed to obtain access token from GitHub.', 'error')
        return redirect(url_for('auth.login'))
    
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    # Get user info from GitHub
    headers = {'Authorization': f'token {access_token}'}
    user_response = requests.get('https://api.github.com/user', headers=headers)
    
    if user_response.status_code != 200:
        flash('Failed to get user information from GitHub.', 'error')
        return redirect(url_for('auth.login'))
    
    user_info = user_response.json()
    
    # Get user email if not public
    email = user_info.get('email')
    if not email:
        email_response = requests.get('https://api.github.com/user/emails', headers=headers)
        if email_response.status_code == 200:
            emails = email_response.json()
            primary_email = next((e for e in emails if e['primary']), None)
            if primary_email:
                email = primary_email['email']
    
    if not email:
        flash('Unable to get email from GitHub. Please make your email public or use manual registration.', 'error')
        return redirect(url_for('auth.login'))
    
    # Find or create user
    user = current_app.db.users.find_one({'email': email})
    
    if user:
        # Update existing user
        current_app.db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
    else:
        # Create new user
        user_data = {
            'name': user_info['name'] or user_info['login'],
            'email': email,
            'avatar': user_info['avatar_url'],
            'provider': 'github',
            'github_id': user_info['id'],
            'github_username': user_info['login'],
            'created_at': datetime.utcnow(),
            'last_login': datetime.utcnow()
        }
        result = current_app.db.users.insert_one(user_data)
        user = current_app.db.users.find_one({'_id': result.inserted_id})
    
    # Set session
    session['user_id'] = str(user['_id'])
    session['user_email'] = user['email']
    session['user_name'] = user['name']
    session['user_avatar'] = user['avatar']
    
    flash(f'Successfully logged in with GitHub! Welcome, {user["name"]}!', 'success')
    return redirect(url_for('dashboard.dashboard'))