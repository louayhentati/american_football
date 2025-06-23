from app.extensions import db
from app.models.user import UserModel
from app.models.play_call import PlayCallModel

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    play_call_id = db.Column(db.Integer, db.ForeignKey('play_call.id', ondelete='SET NULL'), nullable=True)

    user = db.relationship(UserModel, backref=db.backref('preference', uselist=False))
    play_call = db.relationship(PlayCallModel)
