from app.extensions import db

class DriveModel(db.Model):
    __tablename__ = 'drive'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    result = db.Column(db.String(50))
    plays = db.relationship('PlayModel', backref='drive', lazy=True, cascade='all, delete-orphan')
