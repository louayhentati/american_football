import random
from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models.drive import DriveModel
from app.models.team import TeamModel
from app.models.game import GameModel
from run import PlaybookApp


def seed_database():
    """Main function to seed the database with sample NFL data.

    This function creates:
    - 4 randomly selected NFL teams
    - 2 games between those 4 teams with random matchups and times
    - Multiple drives for each game
    """
    app = PlaybookApp().app

    with app.app_context():
        print("Clearing existing data...")
        try:

            db.session.execute(db.text('DELETE FROM play'))
            db.session.query(DriveModel).delete()
            db.session.query(GameModel).delete()
            db.session.query(TeamModel).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing data: {e}")
            raise

        def create_teams():
            """Selects 4 random teams and creates them in the database."""
            # All 32 NFL teams with their official colors
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
            print(f"Created {len(created_teams)} random NFL teams for games.")
            return created_teams

        def create_games(teams):
            """Create 2 games with random matchups and times from the provided teams."""
            if len(teams) < 4:
                print("Need at least 4 teams to create games.")
                return []

            random.shuffle(teams)

            possible_times = ["13:00", "16:05", "16:25", "20:15"]
            game_times = random.sample(possible_times, 2)

            today = datetime.now(timezone.utc)
            last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
            last_sunday = last_sunday.replace(tzinfo=None)

            game1 = GameModel(
                name=f"{teams[1].name} @ {teams[0].name}",  # Away @ Home
                game_date=last_sunday,
                game_time=game_times[0],
                home_team_id=teams[0].id,
                away_team_id=teams[1].id
            )

            game2 = GameModel(
                name=f"{teams[3].name} @ {teams[2].name}",  # Away @ Home
                game_date=last_sunday,
                game_time=game_times[1],
                home_team_id=teams[2].id,
                away_team_id=teams[3].id
            )

            db.session.add_all([game1, game2])
            db.session.commit()
            games = [game1, game2]
            print(f"Created {len(games)} games with random matchups and times.")
            return games

        def create_drives(games):
            """Create a random number of drives for each game."""
            drives = []
            for game in games:
                total_drives_for_game = random.randint(20, 24)
                for _ in range(total_drives_for_game):
                    drive = DriveModel(
                        game_id=game.id,
                        result=None
                    )
                    drives.append(drive)

            db.session.add_all(drives)
            db.session.commit()
            print(f"Created {len(drives)} total drives for the games.")
            return drives

        teams = create_teams()
        games = create_games(teams)
        create_drives(games)

        print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()