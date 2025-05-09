# enhanced_dummy_data.py
from app import app, db
from models import Game, Drive, Play
from datetime import datetime
import random

PERSONNEL_GROUPS = ['10', '11', '20', '21']
RUN_RESULTS = ['Rush', 'Touchdown', 'Fumble']
PASS_RESULTS = ['Complete', 'Incomplete', 'Interception', 'Sack', 'Touchdown']
DRIVE_RESULTS = ['TOUCHDOWN', 'PUNT', 'FIELD GOAL', 'TURNOVER ON DOWNS', 'INTERCEPTION', 'FUMBLE']

# Constants
MIN_PLAYS_PER_DRIVE = 3  # Minimum plays per drive
MAX_PLAYS_PER_DRIVE = 12  # Maximum plays per drive

def create_bronsons_vs_johnsons_game(game_date=datetime(2025, 3, 12)):
    # Start a context to interact with the database
    with app.app_context():
        # Create a new game called "Bronsons vs Johnsons" with a specific date and time
        game = Game(
            game_name='Bronsons vs Johnsons',
            date=game_date,
            time='14:00'
        )
        db.session.add(game)
        db.session.commit()

        # Create 10 drives for this game
        for _ in range(1, 11):
            # Create a new drive (temporary "IN PROGRESS" will be overridden)
            drive = Drive(game_id=game.id, result='IN PROGRESS')
            db.session.add(drive)
            db.session.commit()

            # Determine the starting yard line (random between 20 and 50 on the positive side, offense's territory)
            current_yard_line = random.randint(20, 50)  # Starting on the positive side (left of 50)
            # Random number of plays between MIN_PLAYS_PER_DRIVE and MAX_PLAYS_PER_DRIVE
            num_plays = random.randint(MIN_PLAYS_PER_DRIVE, MAX_PLAYS_PER_DRIVE)
            down = 1
            distance = 10

            # List to store play data for this drive
            plays_data = []
            for play_num in range(1, num_plays + 1):
                # Randomly choose play type (Run or Pass)
                play_type = random.choice(['Run', 'Pass'])
                # Determine result based on play type
                if play_type == 'Run':
                    result = random.choices(RUN_RESULTS, weights=[90, 5, 5])[0]
                else:  # Pass
                    result = random.choices(PASS_RESULTS, weights=[60, 25, 5, 5, 5])[0]

                # Calculate gain/loss (offense moves to the right, so a gain decreases the yard line)
                if result in ['Touchdown', 'Incomplete']:
                    gain_loss = 0
                elif result == 'Sack':
                    gain_loss = -random.randint(1, 8)  # Loss moves yard line to the left (positive direction)
                elif play_type == 'Run':
                    gain_loss = random.randint(1, 10)  # Gain moves yard line to the right (negative direction)
                else:  # Pass
                    gain_loss = random.randint(5, 15)  # Gain moves yard line to the right (negative direction)

                # Update yard line: Offense moves right, so a positive gain decreases the yard line
                if result not in ['Punt', 'Field Goal', 'Missed FG']:
                    if gain_loss > 0:  # Gain: Move toward the right (decrease yard line)
                        current_yard_line -= gain_loss
                    elif gain_loss < 0:  # Loss: Move toward the left (increase yard line)
                        current_yard_line -= gain_loss  # gain_loss is negative, so this increases the yard line
                    # Ensure yard line stays within bounds (-50 to 50)
                    current_yard_line = max(-50, min(50, current_yard_line))

                # Add play data
                plays_data.append({
                    'play_num': play_num,
                    'down': down,
                    'distance': distance,
                    'yard_line': current_yard_line,
                    'play_type': play_type,
                    'result': result,
                    'gain_loss': gain_loss,
                    'personnel': random.choice(PERSONNEL_GROUPS)
                })

                # Update downs and distance
                if gain_loss >= distance:
                    down = 1
                    distance = 10
                else:
                    down += 1
                    distance -= gain_loss if gain_loss > 0 else 0  # Only count gains toward distance

            # Set drive result based on the last play or derived condition
            drive.result = plays_data[-1]['result'] if plays_data[-1]['result'] else "In Progress"

            db.session.commit()

            # Add all plays to the drive
            for play_data in plays_data:
                play = Play(
                    drive_id=drive.id,
                    odk='O',
                    down=play_data['down'],
                    distance=play_data['distance'],
                    yard_line=play_data['yard_line'],
                    play_type=play_data['play_type'],
                    result=play_data['result'],
                    gain_loss=play_data['gain_loss'],
                    personnel=play_data['personnel'],
                    off_form=random.choice(['TRIPS', 'ACE', 'TREY', 'DOUBLES', 'EMPTY']),
                    form_str=random.choice(['LEFT', 'RIGHT', 'WEAK', 'STRONG']),
                    form_adj=random.choice(['WING', 'SLOT', 'WIDE', 'TIGHT']),
                    motion=random.choice(['JET', 'ORBIT', 'SHIFT', 'NONE']),
                    protection=random.choice(['BASE', '2-JET', 'MAX', 'SLIDE']),
                    off_play=random.choice(['DIVE', 'POWER', 'STRETCH', 'SCREEN']),
                    dir_call=random.choice(['LEFT', 'RIGHT', 'MIDDLE']),
                    tag=random.choice(['CHECK', 'ALERT', 'AUTO']),
                    hash=random.choice(['L', 'M', 'R']),
                    touchdown=(play_data['result'] == 'Touchdown' or current_yard_line <= -50)
                )
                db.session.add(play)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing play to the database: {e}")

        print("Bronsons vs Johnsons game with 10 drives created successfully!")

def create_lions_vs_tigers_game(game_date=datetime(2025, 3, 10)):
    # Start a context to interact with the database
    with app.app_context():
        # Create a new game called "Lions vs Tigers" with a specific date and time
        game = Game(
            game_name='Lions vs Tigers',
            date=game_date,
            time='16:00'
        )
        db.session.add(game)
        db.session.commit()

        # Create 10 drives for this game
        for _ in range(1, 11):
            drive = Drive(game_id=game.id, result='IN PROGRESS')
            db.session.add(drive)
            db.session.commit()

            current_yard_line = random.randint(20, 50)  # Starting on the positive side
            num_plays = random.randint(MIN_PLAYS_PER_DRIVE, MAX_PLAYS_PER_DRIVE)
            down = 1
            distance = 10

            plays_data = []
            for play_num in range(1, num_plays + 1):
                play_type = random.choice(['Run', 'Pass'])
                if play_type == 'Run':
                    result = random.choices(RUN_RESULTS, weights=[90, 5, 5])[0]
                else:
                    result = random.choices(PASS_RESULTS, weights=[60, 25, 5, 5, 5])[0]

                if result in ['Touchdown', 'Incomplete']:
                    gain_loss = 0
                elif result == 'Sack':
                    gain_loss = -random.randint(1, 8)
                elif play_type == 'Run':
                    gain_loss = random.randint(1, 10)
                else:
                    gain_loss = random.randint(5, 15)

                if result not in ['Punt', 'Field Goal', 'Missed FG']:
                    if gain_loss > 0:  # Gain: Move toward the right (decrease yard line)
                        current_yard_line -= gain_loss
                    elif gain_loss < 0:  # Loss: Move toward the left (increase yard line)
                        current_yard_line -= gain_loss
                    current_yard_line = max(-50, min(50, current_yard_line))

                plays_data.append({
                    'play_num': play_num,
                    'down': down,
                    'distance': distance,
                    'yard_line': current_yard_line,
                    'play_type': play_type,
                    'result': result,
                    'gain_loss': gain_loss,
                    'personnel': random.choice(PERSONNEL_GROUPS)
                })

                if gain_loss >= distance:
                    down = 1
                    distance = 10
                else:
                    down += 1
                    distance -= gain_loss if gain_loss > 0 else 0

            drive.result = plays_data[-1]['result'] if plays_data[-1]['result'] else "In Progress"
            db.session.commit()

            for play_data in plays_data:
                play = Play(
                    drive_id=drive.id,
                    odk='O',
                    down=play_data['down'],
                    distance=play_data['distance'],
                    yard_line=play_data['yard_line'],
                    play_type=play_data['play_type'],
                    result=play_data['result'],
                    gain_loss=play_data['gain_loss'],
                    personnel=play_data['personnel'],
                    off_form=random.choice(['TRIPS', 'ACE', 'TREY', 'DOUBLES', 'EMPTY']),
                    form_str=random.choice(['LEFT', 'RIGHT', 'WEAK', 'STRONG']),
                    form_adj=random.choice(['WING', 'SLOT', 'WIDE', 'TIGHT']),
                    motion=random.choice(['JET', 'ORBIT', 'SHIFT', 'NONE']),
                    protection=random.choice(['BASE', '2-JET', 'MAX', 'SLIDE']),
                    off_play=random.choice(['DIVE', 'POWER', 'STRETCH', 'SCREEN']),
                    dir_call=random.choice(['LEFT', 'RIGHT', 'MIDDLE']),
                    tag=random.choice(['CHECK', 'ALERT', 'AUTO']),
                    hash=random.choice(['L', 'M', 'R']),
                    touchdown=(play_data['result'] == 'Touchdown' or current_yard_line <= -50)
                )
                db.session.add(play)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing play to the database: {e}")

        print("Lions vs Tigers game with 10 drives created successfully!")

def create_bears_vs_wolves_game(game_date=datetime(2025, 3, 11)):
    # Start a context to interact with the database
    with app.app_context():
        # Create a new game called "Bears vs Wolves" with a specific date and time
        game = Game(
            game_name='Bears vs Wolves',
            date=game_date,
            time='18:00'
        )
        db.session.add(game)
        db.session.commit()

        # Create 10 drives for this game
        for _ in range(1, 11):
            drive = Drive(game_id=game.id, result='IN PROGRESS')
            db.session.add(drive)
            db.session.commit()

            current_yard_line = random.randint(20, 50)  # Starting on the positive side
            num_plays = random.randint(MIN_PLAYS_PER_DRIVE, MAX_PLAYS_PER_DRIVE)
            down = 1
            distance = 10

            plays_data = []
            for play_num in range(1, num_plays + 1):
                play_type = random.choice(['Run', 'Pass'])
                if play_type == 'Run':
                    result = random.choices(RUN_RESULTS, weights=[90, 5, 5])[0]
                else:
                    result = random.choices(PASS_RESULTS, weights=[60, 25, 5, 5, 5])[0]

                if result in ['Touchdown', 'Incomplete']:
                    gain_loss = 0
                elif result == 'Sack':
                    gain_loss = -random.randint(1, 8)
                elif play_type == 'Run':
                    gain_loss = random.randint(1, 10)
                else:
                    gain_loss = random.randint(5, 15)

                if result not in ['Punt', 'Field Goal', 'Missed FG']:
                    if gain_loss > 0:  # Gain: Move toward the right (decrease yard line)
                        current_yard_line -= gain_loss
                    elif gain_loss < 0:  # Loss: Move toward the left (increase yard line)
                        current_yard_line -= gain_loss
                    current_yard_line = max(-50, min(50, current_yard_line))

                plays_data.append({
                    'play_num': play_num,
                    'down': down,
                    'distance': distance,
                    'yard_line': current_yard_line,
                    'play_type': play_type,
                    'result': result,
                    'gain_loss': gain_loss,
                    'personnel': random.choice(PERSONNEL_GROUPS)
                })

                if gain_loss >= distance:
                    down = 1
                    distance = 10
                else:
                    down += 1
                    distance -= gain_loss if gain_loss > 0 else 0

            drive.result = plays_data[-1]['result'] if plays_data[-1]['result'] else "In Progress"

            db.session.commit()

            for play_data in plays_data:
                play = Play(
                    drive_id=drive.id,
                    odk='O',
                    down=play_data['down'],
                    distance=play_data['distance'],
                    yard_line=play_data['yard_line'],
                    play_type=play_data['play_type'],
                    result=play_data['result'],
                    gain_loss=play_data['gain_loss'],
                    personnel=play_data['personnel'],
                    off_form=random.choice(['TRIPS', 'ACE', 'TREY', 'DOUBLES', 'EMPTY']),
                    form_str=random.choice(['LEFT', 'RIGHT', 'WEAK', 'STRONG']),
                    form_adj=random.choice(['WING', 'SLOT', 'WIDE', 'TIGHT']),
                    motion=random.choice(['JET', 'ORBIT', 'SHIFT', 'NONE']),
                    protection=random.choice(['BASE', '2-JET', 'MAX', 'SLIDE']),
                    off_play=random.choice(['DIVE', 'POWER', 'STRETCH', 'SCREEN']),
                    dir_call=random.choice(['LEFT', 'RIGHT', 'MIDDLE']),
                    tag=random.choice(['CHECK', 'ALERT', 'AUTO']),
                    hash=random.choice(['L', 'M', 'R']),
                    touchdown=(play_data['result'] == 'Touchdown' or current_yard_line <= -50)
                )
                db.session.add(play)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing play to the database: {e}")

        print("Bears vs Wolves game with 10 drives created successfully!")

if __name__ == "__main__":
    print("\nCreating Bronsons vs Johnsons game data...")
    create_bronsons_vs_johnsons_game()
    print("\nCreating Lions vs Tigers game data...")
    create_lions_vs_tigers_game()
    print("\nCreating Bears vs Wolves game data...")
    create_bears_vs_wolves_game()
    print("\nSetup complete!")