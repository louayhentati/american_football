from flask_login import UserMixin
from app.extensions import db

class UserModel(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))  
    team = db.relationship('TeamModel', backref='users')

    preference = db.relationship(
        'UserPreference',
        uselist=False,
        cascade='all, delete-orphan',
        passive_deletes=True,
        back_populates='user'
    )
