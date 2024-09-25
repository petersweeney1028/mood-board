from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from models import db, User
from config import Config
import requests

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@auth_bp.route('/auth/instagram')
@login_required
def auth_instagram():
    return redirect(f"https://api.instagram.com/oauth/authorize?client_id={Config.INSTAGRAM_CLIENT_ID}&redirect_uri={Config.INSTAGRAM_REDIRECT_URI}&scope=user_profile,user_media&response_type=code")

@auth_bp.route('/auth/instagram/callback')
@login_required
def instagram_callback():
    code = request.args.get('code')
    data = {
        'client_id': Config.INSTAGRAM_CLIENT_ID,
        'client_secret': Config.INSTAGRAM_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': Config.INSTAGRAM_REDIRECT_URI,
        'code': code
    }
    response = requests.post('https://api.instagram.com/oauth/access_token', data=data)
    if response.status_code == 200:
        access_token = response.json()['access_token']
        current_user.instagram_token = access_token
        db.session.commit()
        flash('Instagram account connected successfully!')
    else:
        flash('Failed to connect Instagram account.')
    return redirect(url_for('index'))

@auth_bp.route('/auth/spotify')
@login_required
def auth_spotify():
    return redirect(f"https://accounts.spotify.com/authorize?client_id={Config.SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={Config.SPOTIFY_REDIRECT_URI}&scope=user-top-read")

@auth_bp.route('/auth/spotify/callback')
@login_required
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
        current_user.spotify_token = access_token
        db.session.commit()
        flash('Spotify account connected successfully!')
    else:
        flash('Failed to connect Spotify account.')
    return redirect(url_for('index'))
