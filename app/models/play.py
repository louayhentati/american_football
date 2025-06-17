from app.extensions import db


class PlayModel(db.Model):
    __tablename__ = 'play'
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
