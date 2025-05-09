# init_db.py
from app import app, db
from models import User, Game, Drive, Play, PlayOption


def init_database():
    with app.app_context():
        # Drop all existing tables
        db.drop_all()

        # Create all tables
        db.create_all()

        # Create a test user
        test_user = User(
            username="coach",
            password="password123"  # In production, use password hashing!
        )
        db.session.add(test_user)

        # Add play options from the data
        play_options = [
            PlayOption(id=1, parameter_name="off_form", value="Right", enabled=True),
            PlayOption(id=2, parameter_name="off_form", value="Left", enabled=True),
            PlayOption(id=3, parameter_name="off_form", value="Trey", enabled=True),
            PlayOption(id=4, parameter_name="off_form", value="Ace", enabled=True),
            PlayOption(id=5, parameter_name="off_form", value="Trips", enabled=True),
            PlayOption(id=6, parameter_name="form_str", value="Right", enabled=True),
            PlayOption(id=7, parameter_name="form_str", value="Left", enabled=True),
            PlayOption(id=8, parameter_name="form_adj", value="Strong", enabled=True),
            PlayOption(id=10, parameter_name="form_adj", value="Strong Wing", enabled=True),
            PlayOption(id=11, parameter_name="form_adj", value="Weak", enabled=True),
            PlayOption(id=12, parameter_name="form_adj", value="Weak Wing", enabled=True),
            PlayOption(id=13, parameter_name="form_adj", value="Weak Slot", enabled=True),
            PlayOption(id=14, parameter_name="motion", value="H-IN", enabled=True),
            PlayOption(id=15, parameter_name="motion", value="H-O", enabled=True),
            PlayOption(id=16, parameter_name="motion", value="W-O", enabled=True),
            PlayOption(id=17, parameter_name="protection", value="30", enabled=True),
            PlayOption(id=18, parameter_name="protection", value="60", enabled=True),
            PlayOption(id=19, parameter_name="off_play", value="Breakfast", enabled=True),
            PlayOption(id=20, parameter_name="off_play", value="Lunch", enabled=True),
            PlayOption(id=21, parameter_name="off_play", value="Fade", enabled=True),
            PlayOption(id=22, parameter_name="off_play", value="Dive", enabled=True),
            PlayOption(id=23, parameter_name="off_play", value="Stick", enabled=True),
            PlayOption(id=24, parameter_name="off_play", value="Stretch", enabled=True),
            PlayOption(id=25, parameter_name="off_play", value="Power", enabled=True),
            PlayOption(id=26, parameter_name="dir_call", value="Green", enabled=True),
            PlayOption(id=27, parameter_name="dir_call", value="Blue", enabled=True),
            PlayOption(id=28, parameter_name="tag", value="Y-Pop", enabled=True)
        ]

        for option in play_options:
            db.session.add(option)

        db.session.commit()

        print("Database initialized with test user and play options!")


if __name__ == "__main__":
    init_database()