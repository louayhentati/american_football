import random
from datetime import datetime, timedelta, timezone

try:
    from app.extensions import db
    from app.models.drive import DriveModel
    from app.models.team import TeamModel
    from app.models.game import GameModel
    from app.models.play import PlayModel
    from run import PlaybookApp
    from app.config import ApplicationData
except (ImportError, ModuleNotFoundError):
    print("Could not import full app context. Using local definitions for seeding.")
    db = None
    DriveModel = None
    TeamModel = None
    GameModel = None
    PlayModel = None
    PlaybookApp = None

    class ApplicationData:
        PLAY_OPTIONS = [
            ("off_form", "Right"), ("off_form", "Left"), ("off_form", "Trey"), ("off_form", "Ace"),
            ("off_form", "Trips"),
            ("form_str", "Right"), ("form_str", "Left"),
            ("form_adj", "Strong"), ("form_adj", "Strong Wing"), ("form_adj", "Weak"),
            ("motion", "H-IN"), ("motion", "H-O"), ("motion", "W-O"), ("motion", "Jet"),
            ("protection", "30"), ("protection", "60"), ("protection", "Slide"),
            ("off_play", "Breakfast"), ("off_play", "Lunch"), ("off_play", "Fade"), ("off_play", "Dive"),
            ("off_play", "Stick"),
            ("dir_call", "Green"), ("dir_call", "Blue"),
            ("tag", "Y-Pop"), ("tag", "Z-Go")
        ]

OFF_FORM_OPTIONS = [opt[1] for opt in ApplicationData.PLAY_OPTIONS if opt[0] == 'off_form']
FORM_STR_OPTIONS = [opt[1] for opt in ApplicationData.PLAY_OPTIONS if opt[0] == 'form_str']
FORM_ADJ_OPTIONS = [opt[1] for opt in ApplicationData.PLAY_OPTIONS if opt[0] == 'form_adj']
MOTION_OPTIONS = [opt[1] for opt in ApplicationData.PLAY_OPTIONS if opt[0] == 'motion']
PROTECTION_OPTIONS = [opt[1] for opt in ApplicationData.PLAY_OPTIONS if opt[0] == 'protection']
OFF_PLAY_OPTIONS = [opt[1] for opt in ApplicationData.PLAY_OPTIONS if opt[0] == 'off_play']
DIR_CALL_OPTIONS = [opt[1] for opt in ApplicationData.PLAY_OPTIONS if opt[0] == 'dir_call']
TAG_OPTIONS = [opt[1] for opt in ApplicationData.PLAY_OPTIONS if opt[0] == 'tag']

PERSONNEL_GROUPS = ['10', '11', '12', '21', '22']
RUN_RESULTS = ['Rush', 'Touchdown', 'Fumble']
PASS_RESULTS = ['Complete', 'Incomplete', 'Interception', 'Sack', 'Touchdown']
MIN_PLAYS_PER_DRIVE = 3
MAX_PLAYS_PER_DRIVE = 12


def seed_database():
    """Seeds the database with sample NFL data, including teams, games, drives, and plays."""
    if not PlaybookApp:
        print("Error: App context could not be loaded. Cannot seed database.")
        return

    app = PlaybookApp().app

    with app.app_context():
        try:
            db.session.query(PlayModel).delete()
            db.session.query(DriveModel).delete()
            db.session.query(GameModel).delete()
            db.session.query(TeamModel).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing data: {e}")
            raise

        teams = create_teams()
        games = create_games(teams)
        if games:
             drives = create_drives_for_games(games)
             create_plays_for_drives(drives)
             print("Games have been successfully created.")


def create_teams():
    """
    Selects 4 random NFL teams from a predefined list and commits them to the database.

    Returns:
        list: A list of the created TeamModel objects.
    """
    nfl_teams_data = [
        {"name": "Arizona Cardinals", "primary_color": "#97233F", "secondary_color": "#000000"},
        {"name": "Atlanta Falcons", "primary_color": "#A71930", "secondary_color": "#000000"},
        {"name": "Baltimore Ravens", "primary_color": "#241773", "secondary_color": "#000000"},
        {"name": "Buffalo Bills", "primary_color": "#00338D", "secondary_color": "#C60C30"},
        {"name": "Carolina Panthers", "primary_color": "#0085CA", "secondary_color": "#101820"},
        {"name": "Chicago Bears", "primary_color": "#0B162A", "secondary_color": "#C83803"},
        {"name": "Cincinnati Bengals", "primary_color": "#FB4F14", "secondary_color": "#000000"},
        {"name": "Cleveland Browns", "primary_color": "#311D00", "secondary_color": "#FF3C00"},
        {"name": "Dallas Cowboys", "primary_color": "#041E42", "secondary_color": "#869397"},
        {"name": "Denver Broncos", "primary_color": "#002244", "secondary_color": "#FB4F14"},
        {"name": "Detroit Lions", "primary_color": "#0076B6", "secondary_color": "#B0B7BC"},
        {"name": "Green Bay Packers", "primary_color": "#203731", "secondary_color": "#FFB612"},
        {"name": "Houston Texans", "primary_color": "#03202F", "secondary_color": "#A71930"},
        {"name": "Indianapolis Colts", "primary_color": "#002C5F", "secondary_color": "#A2AAAD"},
        {"name": "Jacksonville Jaguars", "primary_color": "#006778", "secondary_color": "#9F792C"},
        {"name": "Kansas City Chiefs", "primary_color": "#E31837", "secondary_color": "#FFB81C"},
        {"name": "Las Vegas Raiders", "primary_color": "#000000", "secondary_color": "#A5ACAF"},
        {"name": "Los Angeles Chargers", "primary_color": "#0080C6", "secondary_color": "#FFC20E"},
        {"name": "Los Angeles Rams", "primary_color": "#003594", "secondary_color": "#FFA300"},
        {"name": "Miami Dolphins", "primary_color": "#008E97", "secondary_color": "#FC4C02"},
        {"name": "Minnesota Vikings", "primary_color": "#4F2683", "secondary_color": "#FFC62F"},
        {"name": "New England Patriots", "primary_color": "#002244", "secondary_color": "#C60C30"},
        {"name": "New Orleans Saints", "primary_color": "#D3BC8D", "secondary_color": "#000000"},
        {"name": "New York Giants", "primary_color": "#0B2265", "secondary_color": "#A71930"},
        {"name": "New York Jets", "primary_color": "#003F2D", "secondary_color": "#FFFFFF"},
        {"name": "Philadelphia Eagles", "primary_color": "#004C54", "secondary_color": "#A5ACAF"},
        {"name": "Pittsburgh Steelers", "primary_color": "#FFB612", "secondary_color": "#101820"},
        {"name": "San Francisco 49ers", "primary_color": "#AA0000", "secondary_color": "#B3995D"},
        {"name": "Seattle Seahawks", "primary_color": "#002244", "secondary_color": "#69BE28"},
        {"name": "Tampa Bay Buccaneers", "primary_color": "#D50A0A", "secondary_color": "#FF7900"},
        {"name": "Tennessee Titans", "primary_color": "#0C2340", "secondary_color": "#4B92DB"},
        {"name": "Washington Commanders", "primary_color": "#5A1414", "secondary_color": "#FFB612"}
    ]

    selected_teams_data = random.sample(nfl_teams_data, 4)

    created_teams = []
    for team_data in selected_teams_data:
        team_name_slug = team_data["name"].lower().replace(" ", "_")
        team = TeamModel(
            name=team_data["name"],
            icon=f"/static/images/teams/{team_name_slug}.png",
            primary_color=team_data["primary_color"],
            secondary_color=team_data["secondary_color"]
        )
        db.session.add(team)
        created_teams.append(team)

    db.session.commit()
    return created_teams


def create_games(teams):
    """
    Creates two games with random matchups from the provided list of teams.

    Args:
        teams (list): A list of four or more TeamModel objects.

    Returns:
        list: A list containing the two created GameModel objects.
    """
    if len(teams) < 4:
        return []

    random.shuffle(teams)
    possible_times = ["13:00", "16:05", "16:25", "20:15"]
    game_times = random.sample(possible_times, 2)
    today = datetime.now(timezone.utc)
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    last_sunday = last_sunday.replace(tzinfo=None)

    game1 = GameModel(
        name=f"{teams[1].name} @ {teams[0].name}",
        game_date=last_sunday,
        game_time=game_times[0],
        home_team_id=teams[0].id,
        away_team_id=teams[1].id
    )

    game2 = GameModel(
        name=f"{teams[3].name} @ {teams[2].name}",
        game_date=last_sunday,
        game_time=game_times[1],
        home_team_id=teams[2].id,
        away_team_id=teams[3].id
    )

    db.session.add_all([game1, game2])
    db.session.commit()
    return [game1, game2]


def create_drives_for_games(games):
    """
    Creates a random number of drives for each game.

    Args:
        games (list): A list of GameModel objects.

    Returns:
        list: A list of all created DriveModel objects.
    """
    all_drives = []
    for game in games:
        total_drives_for_game = random.randint(18, 22)
        for i in range(total_drives_for_game):
            drive = DriveModel(
                game_id=game.id,
                result="In Progress"
            )
            all_drives.append(drive)

    db.session.add_all(all_drives)
    db.session.commit()
    return all_drives


def create_plays_for_drives(drives):
    """
    Generates and commits a realistic series of plays for each drive.

    Args:
        drives (list): A list of DriveModel objects.
    """
    for i, drive in enumerate(drives):
        current_yard_line = -random.randint(20, 45)
        down = 1
        distance = 10
        drive_over = False
        final_drive_result = "Punt"
        quarter = min(int((i // (len(drives) / 4)) + 1), 4)

        for play_num in range(1, MAX_PLAYS_PER_DRIVE + 1):
            if drive_over:
                break

            play_type = random.choice(['Run', 'Pass'])

            if play_type == 'Run':
                result = random.choices(RUN_RESULTS, weights=[0.9, 0.05, 0.05])[0]
                gain_loss = random.randint(-3, 9) if result == 'Rush' else 0
            else:
                result = random.choices(PASS_RESULTS, weights=[0.60, 0.25, 0.05, 0.05, 0.05])[0]
                if result == 'Complete':
                    gain_loss = random.randint(3, 25)
                elif result == 'Sack':
                    gain_loss = -random.randint(5, 12)
                else:
                    gain_loss = 0

            is_touchdown = (result == 'Touchdown' or (current_yard_line + gain_loss) >= 50)

            play = PlayModel(
                drive_id=drive.id,
                odk='O',
                quarter=quarter,
                down=down,
                distance=distance,
                yard_line=current_yard_line,
                play_type=play_type,
                result=result,
                gain_loss=gain_loss,
                personnel=random.choice(PERSONNEL_GROUPS),
                off_form=random.choice(OFF_FORM_OPTIONS),
                form_str=random.choice(FORM_STR_OPTIONS),
                form_adj=random.choice(FORM_ADJ_OPTIONS),
                motion=random.choice(MOTION_OPTIONS),
                protection=random.choice(PROTECTION_OPTIONS),
                off_play=random.choice(OFF_PLAY_OPTIONS),
                dir_call=random.choice(DIR_CALL_OPTIONS),
                tag=random.choice(TAG_OPTIONS),
                hash=random.choice(['L', 'M', 'R']),
                touchdown=is_touchdown
            )
            db.session.add(play)

            current_yard_line += gain_loss

            if is_touchdown:
                final_drive_result = "Touchdown"
                drive_over = True
            elif result in ['Interception', 'Fumble']:
                final_drive_result = "Turnover"
                drive_over = True
            elif gain_loss >= distance:
                down = 1
                distance = 10
                if current_yard_line >= 40:
                    distance = 50 - current_yard_line
            else:
                down += 1
                distance -= gain_loss

            if down > 4:
                final_drive_result = "Turnover on Downs"
                drive_over = True

            current_yard_line = max(-50, min(50, current_yard_line))

            if down == 4 and not drive_over and current_yard_line < 35:
                final_drive_result = "Punt"
                drive_over = True

        drive.result = final_drive_result
        drive.ended = True

    db.session.commit()


if __name__ == "__main__":
    seed_database()