from app.extensions import db

class PlayOptionModel(db.Model):
    __tablename__ = 'play_option'

    id = db.Column(db.Integer, primary_key=True)
    parameter_name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    enabled = db.Column(db.Boolean, default=True)

    play_call_id = db.Column(db.Integer, db.ForeignKey('play_call.id'), nullable=True)
    play_call = db.relationship('PlayCallModel', backref='options')

    __table_args__ = (
        db.UniqueConstraint('parameter_name', 'value', name='unique_play_option'),
    )
