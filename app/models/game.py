# from app.extensions import db
#
#
# class GameModel(db.Model):
#     __tablename__ = 'game'
#     id = db.Column(db.Integer, primary_key=True)
#     game_name = db.Column(db.String(100), nullable=False)
#     date = db.Column(db.DateTime, nullable=False)
#     time = db.Column(db.String(20), nullable=False)
#     drives = db.relationship('DriveModel', backref='game', lazy=True, cascade='all, delete-orphan')
# game.py (model)
"""
Game model for managing football games
"""

from datetime import datetime, UTC
from typing import Optional, List, Dict, Any
from app.extensions import db


class GameModel(db.Model):
    """Game model for managing football games"""

    __tablename__ = 'game'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    date: datetime = db.Column(db.DateTime, nullable=False, index=True)
    time: str = db.Column(db.String(20), nullable=False)

    home_team_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True, index=True)
    away_team_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True, index=True)

    # Additional Metadata for further development
    # created_at: datetime = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    # updated_at: datetime = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    created_at: datetime = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC).replace(microsecond=0),
        nullable=False
    )

    updated_at: datetime = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC).replace(microsecond=0),
        onupdate=lambda: datetime.now(UTC).replace(microsecond=0)
    )

    # Relationships
    home_team = db.relationship('TeamModel', foreign_keys=[home_team_id], lazy=True)
    away_team = db.relationship('TeamModel', foreign_keys=[away_team_id], lazy=True)
    drives = db.relationship('DriveModel', backref='game', lazy=True, cascade='all, delete-orphan')

    def __init__(
            self,
            name: str,
            game_date: datetime,
            game_time: str,
            home_team_id: Optional[int] = None,
            away_team_id: Optional[int] = None,
    ) -> None:
        """Initialize a new game"""
        self.name = name
        self.date = game_date
        self.time = game_time
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id

    def __repr__(self) -> str:
        """Useful for print(game)"""
        return f'<Game {self.name} on {self.date}>'

    def to_dict(self) -> Dict[str, Any]:
        """Convert game to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'time': self.time,
            'home_team_id': self.home_team_id,
            'away_team_id': self.away_team_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def total_drives(self) -> int:
        """Get total number of drives in this game"""
        return len(self.drives)

    @property
    def total_plays(self) -> int:
        """Get total number of plays in this game"""
        return sum(len(drive.plays) for drive in self.drives)

    @property
    def home_team_name(self) -> Optional[str]:
        """Get the name of the home team"""
        return self.home_team.name if self.home_team else None

    @property
    def away_team_name(self) -> Optional[str]:
        """Get the name of the away team"""
        return self.away_team.name if self.away_team else None

    @classmethod
    def get_by_id(cls, game_id: int) -> Optional['GameModel']:
        """Get game by id"""
        return cls.query.get_or_404(game_id)

    @classmethod
    def get_by_away_team(cls, away_team_id: int) -> Optional['GameModel']:
        """Get game away team id"""
        return cls.query.get_or_404(away_team_id)

    @classmethod
    def get_by_home_team(cls, home_team_id: int) -> Optional['GameModel']:
        """Get game by home team id"""
        return cls.query.get_or_404(home_team_id)

    @classmethod
    def get_by_date_range(cls, start_date: date, end_date: date) -> List['GameModel']:
        """Get games within a date range"""
        return cls.query.filter(cls.date.between(start_date, end_date)).all()

    @classmethod
    def get_recent_games(cls, limit: int = 10) -> List['GameModel']:
        """Get recent games"""
        return cls.query.order_by(cls.date.desc()).limit(limit).all()

    @classmethod
    def get_games_by_team(cls, team_id: int) -> List['GameModel']:
        """Get games for a specific team"""
        return cls.query.filter(
            (cls.home_team_id == team_id) | (cls.away_team_id == team_id)
        ).all()
