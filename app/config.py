class ServerConfig:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///football.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ApplicationData:
    PLAY_CALLS = ['RPO', 'PASS', 'SCREEN', 'RUN']
    PLAY_PARAMETERS = {
        'off_form': 'Offensive Formation',
        'form_str': 'Formation Strength',
        'form_adj': 'Formation Adjustment',
        'motion': 'Motion',
        'protection': 'Protection',
        'off_play': 'Off Play',
        'dir_call': 'Directional Call',
        'tag': 'Tags'
    }

    PLAY_OPTIONS = [
        ("off_form", "Right"),
        ("off_form", "Left"),
        ("off_form", "Trey"),
        ("off_form", "Ace"),
        ("off_form", "Trips"),
        ("form_str", "Right"),
        ("form_str", "Left"),
        ("form_adj", "Strong"),
        ("form_adj", "Strong Wing"),
        ("form_adj", "Weak"),
        ("form_adj", "Weak Wing"),
        ("form_adj", "Weak Slot"),
        ("motion", "H-IN"),
        ("motion", "H-O"),
        ("motion", "W-O"),
        ("protection", "30"),
        ("protection", "60"),
        ("off_play", "Breakfast"),
        ("off_play", "Lunch"),
        ("off_play", "Fade"),
        ("off_play", "Dive"),
        ("off_play", "Stick"),
        ("off_play", "Stretch"),
        ("off_play", "Power"),
        ("dir_call", "Green"),
        ("dir_call", "Blue"),
        ("tag", "Y-Pop"),
        ("tag", "Y-Pop"),

        ("coverage", "Cover 2"),
        ("coverage", "Cover 2 Man"),
        ("coverage", "Cover 3"),
        ("coverage", "Cover 3 Sky"),
        ("coverage", "Cover 3 Buzz"),
        ("coverage", "Cover 4"),
        ("coverage", "Cover 6"),

        ("defense_front", "3-4"),
        ("defense_front", "4-3"),
        ("defense_front", "3-3-5"),
        ("defense_strongside", "Ringo"),
        ("defense_strongside", "Louie"),
        ("blitz", "Mike A"),
        ("blitz", "Sam B"),
        ("blitz", "Will C"),
        ("slants", "Pinch"),
        ("slants", "Slant"),
        ("dir_call", "Green"),
        ("dir_call", "Blue"),

        ("play_type1", "Run"),
        ("play_type1", "Pass"),
        ("play_type1", "2-Point"),
    ]

    DRIVE_ENDING_RESULTS = [
        'Touchdown', 'Rush, TD', 'Complete, TD',
        'Interception', 'Interception, Def TD', 'Fumble',
        'Fumble, Def TD', 'Punt'
    ]
