# Gaivy, Hamza
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):  # Add UserMixin here
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    drives = db.relationship('Drive', backref='game', lazy=True, cascade="all, delete-orphan")


class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    result = db.Column(db.String(50))
    plays = db.relationship('Play', backref='drive', lazy=True, cascade="all, delete-orphan")


class Play(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)

    # Basic play information
    odk = db.Column(db.String(1))  # O, D, or K
    quarter = db.Column(db.Integer)
    down = db.Column(db.Integer)
    distance = db.Column(db.Integer)
    yard_line = db.Column(db.Integer)
    play_type = db.Column(db.String(50))
    result = db.Column(db.String(50))
    gain_loss = db.Column(db.Integer)
    touchdown = db.Column(db.Boolean, default=False)

    # Formation and personnel
    personnel = db.Column(db.String(20))
    off_form = db.Column(db.String(50))  # Offensive Formation
    form_str = db.Column(db.String(50))  # Formation Strength
    form_adj = db.Column(db.String(50))  # Formation Adjustment

    # Play specifics
    motion = db.Column(db.String(50))  # Motion
    protection = db.Column(db.String(50))  # Protection
    off_play = db.Column(db.String(50))  # Off Play
    dir_call = db.Column(db.String(50))  # Directional Call
    tag = db.Column(db.String(50))  # Tags
    hash = db.Column(db.String(1))  # New field for Hash (L, M, R)


class PlayOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parameter_name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    enabled = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('parameter_name', 'value', name='unique_play_option'),
    )