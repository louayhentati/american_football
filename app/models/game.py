from app.extensions import db


class GameModel(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    drives = db.relationship('DriveModel', backref='game', lazy=True, cascade='all, delete-orphan')
