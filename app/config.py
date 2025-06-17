class ServerConfig:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///football.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ApplicationData:
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
        ("tag", "Y-Pop")
    ]

    TEAMS_DATA = {
        "Rüsselsheim Crusaders": {
            "logo": "/static/assets/crusaders.png",
            "primary": "#5C1D28",
            "secondary": "#FFD200"
        },
        "Arizona Cardinals": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/ARI",
            "primary": "#97233F",
            "secondary": "#000000"
        },
        "Atlanta Falcons": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/ATL",
            "primary": "#A71930",
            "secondary": "#000000"
        },
        "Baltimore Ravens": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/BAL",
            "primary": "#241773",
            "secondary": "#9E7C0C"
        },
        "Buffalo Bills": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/BUF",
            "primary": "#00338D",
            "secondary": "#C60C30"
        },
        "Carolina Panthers": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/CAR",
            "primary": "#0085CA",
            "secondary": "#101820"
        },
        "Chicago Bears": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/CHI",
            "primary": "#0B162A",
            "secondary": "#C83803"
        },
        "Cincinnati Bengals": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/CIN",
            "primary": "#FB4F14",
            "secondary": "#000000"
        },
        "Cleveland Browns": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/CLE",
            "primary": "#311D00",
            "secondary": "#FF3C00"
        },
        "Dallas Cowboys": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/DAL",
            "primary": "#002244",
            "secondary": "#FFFFFF"
        },
        "Denver Broncos": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/DEN",
            "primary": "#FB4F14",
            "secondary": "#002244"
        },
        "Detroit Lions": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/DET",
            "primary": "#0076B6",
            "secondary": "#B0B7BC"
        },
        "Green Bay Packers": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/GB",
            "primary": "#203731",
            "secondary": "#FFB612"
        },
        "Houston Texans": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/HOU",
            "primary": "#03202F",
            "secondary": "#A71930"
        },
        "Indianapolis Colts": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/IND",
            "primary": "#002C5F",
            "secondary": "#FFFFFF"
        },
        "Jacksonville Jaguars": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/JAX",
            "primary": "#006778",
            "secondary": "#D7A22A"
        },
        "Kansas City Chiefs": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/KC",
            "primary": "#E31837",
            "secondary": "#FFB612"
        },
        "Las Vegas Raiders": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/LV",
            "primary": "#000000",
            "secondary": "#A5ACAF"
        },
        "Los Angeles Chargers": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/LAC",
            "primary": "#002A5E",
            "secondary": "#FFC20E"
        },
        "Los Angeles Rams": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/LAR",
            "primary": "#003594",
            "secondary": "#FFA300"
        },
        "Miami Dolphins": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/MIA",
            "primary": "#008E97",
            "secondary": "#F58220"
        },
        "Minnesota Vikings": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/MIN",
            "primary": "#4F2683",
            "secondary": "#FFC62F"
        },
        "New England Patriots": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/NE",
            "primary": "#002244",
            "secondary": "#C60C30"
        },
        "New Orleans Saints": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/NO",
            "primary": "#D3BC8D",
            "secondary": "#000000"
        },
        "New York Giants": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/NYG",
            "primary": "#0B2265",
            "secondary": "#A71930"
        },
        "New York Jets": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/NYJ",
            "primary": "#125740",
            "secondary": "#FFFFFF"
        },
        "Philadelphia Eagles": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/PHI",
            "primary": "#004C54",
            "secondary": "#A5ACAF"
        },
        "Pittsburgh Steelers": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/PIT",
            "primary": "#FFB612",
            "secondary": "#000000"
        },
        "San Francisco 49ers": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/SF",
            "primary": "#AA0000",
            "secondary": "#B3995D"
        },
        "Seattle Seahawks": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/SEA",
            "primary": "#002244",
            "secondary": "#69BE28"
        },
        "Tampa Bay Buccaneers": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/TB",
            "primary": "#D50A0A",
            "secondary": "#0A0A08"
        },
        "Tennessee Titans": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/TEN",
            "primary": "#0C2340",
            "secondary": "#4B92DB"
        },
        "Washington Commanders": {
            "logo": "https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/WAS",
            "primary": "#5A1414",
            "secondary": "#FFB612"
        }
    }
