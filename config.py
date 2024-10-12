import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Spotify API credentials
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    
    # Updated Spotify Redirect URI
    SPOTIFY_REDIRECT_URI = "http://student-hub-petersweeney102.replit.app/auth/spotify/callback"

print(f'Spotify Redirect URI: {Config.SPOTIFY_REDIRECT_URI}')

# Reminder for the user
print("IMPORTANT: Please update this new URL in your Spotify Developer Dashboard.")
