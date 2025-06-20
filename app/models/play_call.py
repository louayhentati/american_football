from app.extensions import db


class PlayCallModel(db.Model):
    __tablename__ = 'play_call'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('name', name='unique_play_call'),
    )
