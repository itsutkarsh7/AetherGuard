# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, session, flash, request, current_app, jsonify
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from bson import ObjectId
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Initialize OAuth
oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    
    # Google OAuth Configuration
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_OAUTH_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_OAUTH_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    # GitHub OAuth Configuration
    oauth.register(
        name='github',
        client_id=app.config.get('GITHUB_OAUTH_CLIENT_ID'),
        client_secret=app.config.get('GITHUB_OAUTH_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'}
    )

@auth_bp.route('/login')
def login():
    """Display login page"""
    return render_template('login.html')

@auth_bp.route('/register')
def register():
    """Display registration page"""
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    """Handle email/password login"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Please fill in all fields', 'error')
        return redirect(url_for('auth.login'))
    
    # Find user in database
    user = current_app.db.users.find_one({'email': email})
    
    if user and check_password_hash(user.get('password', ''), password):
        # Login successful
        session['user_id'] = str(user['_id'])
        session['user_email'] = user['email']
        session['user_name'] = user.get('name', user['email'])
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard.index'))
    else:
        flash('Invalid email or password', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['POST'])
def register_post():
    """Handle user registration"""
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not username or not email or not password:
        flash('Please fill in all fields', 'error')
        return redirect(url_for('auth.register'))
    
    # Check if user already exists
    if current_app.db.users.find_one({'email': email}):
        flash('Email already registered', 'error')
        return redirect(url_for('auth.register'))
    
    # Create new user
    user_data = {
        'username': username,
        'email': email,
        'password': generate_password_hash(password),
        'created_at': datetime.utcnow(),
        'oauth_provider': None
    }
    
    try:
        result = current_app.db.users.insert_one(user_data)
        session['user_id'] = str(result.inserted_id)
        session['user_email'] = email
        session['user_name'] = username
        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard.index'))
    except Exception as e:
        flash('Registration failed. Please try again.', 'error')
        return redirect(url_for('auth.register'))

# Google OAuth Routes
@auth_bp.route('/auth/google')
def google_login():
    """Redirect to Google OAuth"""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            email = user_info['email']
            name = user_info.get('name', email)
            google_id = user_info['sub']
            
            # Check if user exists
            user = current_app.db.users.find_one({'email': email})
            
            if not user:
                # Create new user
                user_data = {
                    'email': email,
                    'name': name,
                    'google_id': google_id,
                    'oauth_provider': 'google',
                    'created_at': datetime.utcnow()
                }
                result = current_app.db.users.insert_one(user_data)
                user_id = str(result.inserted_id)
            else:
                # Update existing user with Google ID if not present
                if not user.get('google_id'):
                    current_app.db.users.update_one(
                        {'_id': user['_id']},
                        {'$set': {'google_id': google_id, 'oauth_provider': 'google'}}
                    )
                user_id = str(user['_id'])
            
            # Set session
            session['user_id'] = user_id
            session['user_email'] = email
            session['user_name'] = name
            flash('Successfully logged in with Google!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Failed to get user information from Google', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        print(f"Google OAuth error: {e}")
        flash('Google login failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

# GitHub OAuth Routes
@auth_bp.route('/auth/github')
def github_login():
    """Redirect to GitHub OAuth"""
    redirect_uri = url_for('auth.github_callback', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        token = oauth.github.authorize_access_token()
        
        # Get user info from GitHub API
        resp = oauth.github.get('user', token=token)
        user_info = resp.json()
        
        # Get user email (might be private)
        email_resp = oauth.github.get('user/emails', token=token)
        emails = email_resp.json()
        
        # Find primary email
        primary_email = None
        for email_data in emails:
            if email_data.get('primary', False):
                primary_email = email_data['email']
                break
        
        if not primary_email and emails:
            primary_email = emails[0]['email']
        
        if user_info and primary_email:
            email = primary_email
            name = user_info.get('name') or user_info.get('login', email)
            github_id = user_info['id']
            
            # Check if user exists
            user = current_app.db.users.find_one({'email': email})
            
            if not user:
                # Create new user
                user_data = {
                    'email': email,
                    'name': name,
                    'github_id': github_id,
                    'oauth_provider': 'github',
                    'created_at': datetime.utcnow()
                }
                result = current_app.db.users.insert_one(user_data)
                user_id = str(result.inserted_id)
            else:
                # Update existing user with GitHub ID if not present
                if not user.get('github_id'):
                    current_app.db.users.update_one(
                        {'_id': user['_id']},
                        {'$set': {'github_id': github_id, 'oauth_provider': 'github'}}
                    )
                user_id = str(user['_id'])
            
            # Set session
            session['user_id'] = user_id
            session['user_email'] = email
            session['user_name'] = name
            flash('Successfully logged in with GitHub!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Failed to get user information from GitHub', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        print(f"GitHub OAuth error: {e}")
        flash('GitHub login failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    """Log out user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('landing.index'))

@auth_bp.route('/profile')
def profile():
    """User profile page (requires login)"""
    if 'user_id' not in session:
        flash('Please log in to access your profile', 'error')
        return redirect(url_for('auth.login'))
    
    user = current_app.db.users.find_one({'_id': ObjectId(session['user_id'])})
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('profile.html', user=user)

# Helper function to check if user is authenticated
def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
