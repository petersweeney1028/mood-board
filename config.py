import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Spotify API credentials
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    
    # Update the SPOTIFY_REDIRECT_URI to use the new deployment URL
    REPL_SLUG = os.environ.get('REPL_SLUG', '')
    REPL_OWNER = os.environ.get('REPL_OWNER', '')
    SPOTIFY_REDIRECT_URI = f"https://{REPL_SLUG}.{REPL_OWNER}.repl.co/auth/spotify/callback"
