from flask import Blueprint, redirect, session, url_for, render_template
import os
from authlib.integrations.flask_client import OAuth
from .utils import get_db, register_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
oauth = OAuth()

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'email profile'},
)

github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_OAUTH_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

@auth_bp.record_once
def setup(state):
    oauth.init_app(state.app)

@auth_bp.route('/login')
def login():
    return render_template("login.html")

@auth_bp.route('/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    session['user'] = {'email': user_info['email'], 'name': user_info['name']}
    register_user(user_info['email'], user_info['name'])
    return redirect(url_for('dashboard.dashboard'))

@auth_bp.route('/github')
def github_login():
    redirect_uri = url_for('auth.github_callback', _external=True)
    return github.authorize_redirect(redirect_uri)

@auth_bp.route('/github/callback')
def github_callback():
    token = github.authorize_access_token()
    user_info = github.get('user').json()
    session['user'] = {'email': user_info['email'], 'name': user_info['name'] or user_info['login']}
    register_user(user_info['email'], user_info['name'])
    return redirect(url_for('dashboard.dashboard'))

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('landing.landing'))
