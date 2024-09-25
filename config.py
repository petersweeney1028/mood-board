import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Instagram API credentials (you need to set these up)
    INSTAGRAM_CLIENT_ID = 'your_instagram_client_id'
    INSTAGRAM_CLIENT_SECRET = 'your_instagram_client_secret'
    INSTAGRAM_REDIRECT_URI = 'http://localhost:5000/auth/instagram/callback'
    
    # Spotify API credentials (you need to set these up)
    SPOTIFY_CLIENT_ID = 'your_spotify_client_id'
    SPOTIFY_CLIENT_SECRET = 'your_spotify_client_secret'
    SPOTIFY_REDIRECT_URI = 'http://localhost:5000/auth/spotify/callback'
