from flask import Blueprint, redirect, url_for, request, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from extensions import db
from config import Config
import requests
import logging

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
    return redirect(f"https://accounts.spotify.com/authorize?client_id={Config.SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={Config.SPOTIFY_REDIRECT_URI}&scope=user-top-read&show_dialog=true")

@auth_bp.route('/auth/spotify/callback')
def spotify_callback():
    error = request.args.get('error')
    if error:
        current_app.logger.error(f"Spotify authentication error: {error}")
        flash(f"Failed to connect Spotify account: {error}", 'error')
        return redirect(url_for('index'))

    code = request.args.get('code')
    if not code:
        current_app.logger.error("No authorization code received from Spotify")
        flash("Failed to connect Spotify account: No authorization code received", 'error')
        return redirect(url_for('index'))

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': Config.SPOTIFY_REDIRECT_URI,
        'client_id': Config.SPOTIFY_CLIENT_ID,
        'client_secret': Config.SPOTIFY_CLIENT_SECRET
    }
    try:
        response = requests.post('https://accounts.spotify.com/api/token', data=data)
        response.raise_for_status()
        access_token = response.json()['access_token']
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error obtaining Spotify access token: {str(e)}")
        flash("Failed to connect Spotify account: Unable to obtain access token", 'error')
        return redirect(url_for('index'))

    try:
        user_info = get_spotify_user_info(access_token)
        if not user_info:
            raise ValueError("Unable to fetch user info from Spotify")
        
        user = User.query.filter_by(username=user_info['id']).first()
        if not user:
            user = User(username=user_info['id'], spotify_token=access_token)
            db.session.add(user)
        else:
            user.spotify_token = access_token
        db.session.commit()
        login_user(user)
        flash('Spotify account connected successfully!', 'success')
    except Exception as e:
        current_app.logger.error(f"Error processing Spotify user info: {str(e)}")
        flash("Failed to connect Spotify account: Unable to process user information", 'error')
        return redirect(url_for('index'))

    return redirect(url_for('index'))

def get_spotify_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching Spotify user info: {str(e)}")
        return None
