import logging
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager
from models import User
from auth import auth_bp
from wallpaper import wallpaper_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(wallpaper_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        return render_template('index.html')

    with app.app_context():
        app.logger.info(f"SPOTIFY_REDIRECT_URI: {Config.SPOTIFY_REDIRECT_URI}")
        app.logger.info(f"SPOTIFY_CLIENT_ID is set: {'Yes' if Config.SPOTIFY_CLIENT_ID else 'No'}")
        app.logger.info(f"SPOTIFY_CLIENT_SECRET is set: {'Yes' if Config.SPOTIFY_CLIENT_SECRET else 'No'}")

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Use the PORT environment variable provided by Replit Deployments
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
