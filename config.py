import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Spotify API credentials
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    
    # Use an environment variable for the base URL
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    SPOTIFY_REDIRECT_URI = f"{BASE_URL}/auth/spotify/callback"

print(f'Spotify Redirect URI: {Config.SPOTIFY_REDIRECT_URI}')
