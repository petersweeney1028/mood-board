from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from config import Config
from models import db, User
from auth import auth_bp
from wallpaper import wallpaper_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.auth_instagram'

app.register_blueprint(auth_bp)
app.register_blueprint(wallpaper_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html')
    elif not current_user.instagram_token:
        return redirect(url_for('auth.auth_instagram'))
    elif not current_user.spotify_token:
        return redirect(url_for('auth.connect_spotify'))
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
