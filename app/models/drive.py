from app.extensions import db
from app.models.play import PlayModel
from app.config import ApplicationData

class DriveModel(db.Model):
    __tablename__ = 'drive'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    result = db.Column(db.String(50))
    ended = db.Column(db.Boolean, default=False)
    plays = db.relationship('PlayModel', backref='drive', lazy=True, cascade='all, delete-orphan')

    def update_status(self):
        last_play = PlayModel.query.filter_by(drive_id=self.id).order_by(PlayModel.id.desc()).first()

        if not last_play:
            self.ended = False
            self.result = "In Progress"
            db.session.commit()
            return

        self.result = last_play.result

        is_turnover_on_downs = (
            last_play.down == 4 and
            last_play.gain_loss is not None and
            last_play.distance is not None and
            last_play.gain_loss < last_play.distance
        )
        is_drive_ending_result = last_play.result in ApplicationData.DRIVE_ENDING_RESULTS

        if is_drive_ending_result or is_turnover_on_downs:
            self.ended = True
        else:
            self.ended = False

        db.session.commit()