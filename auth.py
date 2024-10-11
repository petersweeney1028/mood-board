from flask import Blueprint, redirect, url_for, request, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from extensions import db
from config import Config
import requests
import logging
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    current_app.logger.info("User initiated login process")
    return redirect(url_for('auth.auth_spotify'))

@auth_bp.route('/logout')
@login_required
def logout():
    current_app.logger.info(f"User {current_user.id} logged out")
    logout_user()
    return redirect(url_for('index'))

@auth_bp.route('/auth/spotify')
def auth_spotify():
    spotify_auth_url = f"https://accounts.spotify.com/authorize?client_id={Config.SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={Config.SPOTIFY_REDIRECT_URI}&scope=user-top-read&show_dialog=true"
    current_app.logger.info(f"Redirecting user to Spotify auth URL: {spotify_auth_url}")
    return redirect(spotify_auth_url)

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

    current_app.logger.info(f"Received Spotify authorization code: {code[:10]}...")

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': Config.SPOTIFY_REDIRECT_URI,
        'client_id': Config.SPOTIFY_CLIENT_ID,
        'client_secret': Config.SPOTIFY_CLIENT_SECRET
    }
    try:
        current_app.logger.info("Attempting to exchange code for access token")
        response = requests.post('https://accounts.spotify.com/api/token', data=data)
        response.raise_for_status()
        access_token = response.json()['access_token']
        current_app.logger.info("Successfully obtained Spotify access token")
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error obtaining Spotify access token: {str(e)}")
        flash("Failed to connect Spotify account: Unable to obtain access token", 'error')
        return redirect(url_for('index'))

    try:
        current_app.logger.info("Fetching Spotify user info")
        user_info = get_spotify_user_info(access_token)
        if not user_info:
            raise ValueError("Unable to fetch user info from Spotify")
        
        current_app.logger.info(f"Spotify user info received for user ID: {user_info['id']}")
        user = User.query.filter_by(username=user_info['id']).first()
        if not user:
            current_app.logger.info(f"Creating new user with Spotify ID: {user_info['id']}")
            user = User(username=user_info['id'], spotify_token=access_token)
            db.session.add(user)
        else:
            current_app.logger.info(f"Updating existing user with Spotify ID: {user_info['id']}")
            user.spotify_token = access_token
        db.session.commit()
        login_user(user)
        flash('Spotify account connected successfully!', 'success')
        current_app.logger.info(f"User {user.id} logged in successfully")
    except Exception as e:
        current_app.logger.error(f"Error processing Spotify user info: {str(e)}")
        flash("Failed to connect Spotify account: Unable to process user information", 'error')
        return redirect(url_for('index'))

    return redirect(url_for('index'))

def get_spotify_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        current_app.logger.info("Sending request to Spotify API for user info")
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        response.raise_for_status()
        current_app.logger.info("Successfully received user info from Spotify API")
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching Spotify user info: {str(e)}")
        return None

# Log environment variables (excluding sensitive information)
current_app.logger.info(f"SPOTIFY_REDIRECT_URI: {Config.SPOTIFY_REDIRECT_URI}")
current_app.logger.info(f"SPOTIFY_CLIENT_ID is set: {'Yes' if Config.SPOTIFY_CLIENT_ID else 'No'}")
current_app.logger.info(f"SPOTIFY_CLIENT_SECRET is set: {'Yes' if Config.SPOTIFY_CLIENT_SECRET else 'No'}")
