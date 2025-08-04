from flask import Blueprint, redirect, request, session, url_for
from authlib.integrations.flask_client import OAuth
import os

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()

def configure_oauth(app):
    oauth.init_app(app)

    # Google OAuth setup
    oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        access_token_url='https://oauth2.googleapis.com/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params={'access_type': 'offline', 'prompt': 'consent'},
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},
    )

    # GitHub OAuth setup
    oauth.register(
        name='github',
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        userinfo_endpoint='https://api.github.com/user',
        client_kwargs={'scope': 'user:email'},
    )

@auth_bp.route('/login')
def login():
    return '''
    <div class="text-center mt-10">
        <a href="/auth/login/google" class="text-white bg-red-600 px-4 py-2 rounded hover:bg-red-700">Login with Google</a><br><br>
        <a href="/auth/login/github" class="text-white bg-gray-800 px-4 py-2 rounded hover:bg-gray-900">Login with GitHub</a>
    </div>
    '''

@auth_bp.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo').json()
    session['user'] = {
        'name': user_info['name'],
        'email': user_info['email'],
        'provider': 'google'
    }
    return redirect(url_for('dashboard.dashboard'))

@auth_bp.route('/login/github')
def login_github():
    redirect_uri = url_for('auth.github_callback', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@auth_bp.route('/login/github/callback')
def github_callback():
    token = oauth.github.authorize_access_token()
    user_info = oauth.github.get('user').json()
    session['user'] = {
        'name': user_info['login'],
        'email': user_info.get('email', 'Not Provided'),
        'provider': 'github'
    }
    return redirect(url_for('dashboard.dashboard'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing.landing'))
