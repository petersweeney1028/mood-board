from flask import Blueprint, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from extensions import db
from config import Config
import requests

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return redirect(url_for('auth.auth_spotify'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@auth_bp.route('/auth/spotify')
def auth_spotify():
    return redirect(f"https://accounts.spotify.com/authorize?client_id={Config.SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={Config.SPOTIFY_REDIRECT_URI}&scope=user-top-read")

@auth_bp.route('/auth/spotify/callback')
def spotify_callback():
    code = request.args.get('code')
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': Config.SPOTIFY_REDIRECT_URI,
        'client_id': Config.SPOTIFY_CLIENT_ID,
        'client_secret': Config.SPOTIFY_CLIENT_SECRET
    }
    response = requests.post('https://accounts.spotify.com/api/token', data=data)
    if response.status_code == 200:
        access_token = response.json()['access_token']
        user_info = get_spotify_user_info(access_token)
        user = User.query.filter_by(username=user_info['id']).first()
        if not user:
            user = User(username=user_info['id'], spotify_token=access_token)
            db.session.add(user)
        else:
            user.spotify_token = access_token
        db.session.commit()
        login_user(user)
        flash('Spotify account connected successfully!')
    else:
        flash('Failed to connect Spotify account.')
    return redirect(url_for('index'))

def get_spotify_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    if response.status_code == 200:
        return response.json()
    return None
