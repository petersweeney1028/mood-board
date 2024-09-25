from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instagram_token = db.Column(db.String(255), unique=True)
    spotify_token = db.Column(db.String(255))
