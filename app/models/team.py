from app.extensions import db

class TeamModel(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    primary_color = db.Column(db.String(20), nullable=False)
    secondary_color = db.Column(db.String(20), nullable=False)
