import csv
from datetime import datetime
import io

from flask import Flask, render_template, request, redirect, url_for, flash, make_response, Response
from flask_login import login_required
from app.extensions import db
from app.models.drive import DriveModel
from app.models.game import GameModel
from app.models.play import PlayModel
from app.models.team import TeamModel
from collections import Counter

class GameController:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule(rule='/games', view_func=self.game_options)
        self.app.add_url_rule(rule='/games/<int:game_id>', view_func=self.game_detail)
        self.app.add_url_rule(rule='/games/add', view_func=self.add_game, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/games/<int:game_id>/delete', view_func=self.delete_game, methods=['POST'])
        self.app.add_url_rule(rule='/games/<int:game_id>/add-drive', view_func=self.add_drive, methods=['POST'])
        self.app.add_url_rule(rule='/games/<int:game_id>/drive-chart', view_func=self.drive_chart)
        self.app.add_url_rule(rule='/games/<int:game_id>/export', view_func=self.export_game)
        self.app.add_url_rule(rule='/games/<int:game_id>/drive/<int:drive_id>/play-chart',
                              view_func=self.drive_play_chart)
        self.app.add_url_rule(rule='/filter_drives', view_func=self.filter_drives)
        self.app.add_url_rule(rule='/filter_games', view_func=self.filter_games, methods=['GET'])
        self.app.add_url_rule(rule='/game/<int:game_id>/dashboard', view_func=self.dashboard)
        self.app.add_url_rule(rule='/game/<int:game_id>/dashboard-data',view_func=self.dashboard_data)

    @login_required
    def filter_games(self):
        selected_team = request.args.get('Team')
        print(selected_team)
        games = GameModel.query
        if selected_team:
            games = games.join(GameModel.away_team).filter(TeamModel.name == selected_team)

        return render_template("game/partials/_game_rows.html", games=games.all())

    @login_required
    def dashboard_data(self,game_id):
        odk_filter = request.args.get("odk", "")

        game = GameModel.get_by_id(game_id)
        all_drives = [d for d in game.drives if d.plays]

        if odk_filter:
            drives = [d for d in all_drives if d.plays[0].odk == odk_filter]
        else:
            drives = all_drives

        offense_drives = [d for d in drives if d.plays[0].odk == "O"]
        defense_drives = [d for d in drives if d.plays[0].odk == "D"]
        special_drives = [d for d in drives if d.plays[0].odk == "K"]
        total_plays = sum(len(d.plays) for d in drives)

        return {
            "total_drives": len(drives),
            "offense_drives": len(offense_drives),
            "defense_drives": len(defense_drives),
            "special_drives": len(special_drives),
            "total_plays": total_plays
        }

    @login_required
    def dashboard(self, game_id):
        play_mapping = {
            # PASS-Plays
            'Breakfast': 'PASS',

            # RUN-Plays
            'Dive': 'RUN',
            'Fade': 'RUN',
            'Stick': 'RUN',

            # RPO-Plays
            'Stretch': "RPO",

            # SCREEN-Plays
            'Lunch': 'SCREEN',
            'Power': 'SCREEN',
        }

        game = GameModel.get_by_id(game_id)
        odk_filter = request.args.get("odk")

        if odk_filter:
            filtered_drives = [d for d in game.drives if d.plays and d.plays[0].odk == odk_filter]
        else:
            filtered_drives = game.drives

        offense_drives = [d for d in filtered_drives if d.plays and d.plays[0].odk == 'O']
        defense_drives = [d for d in filtered_drives if d.plays and d.plays[0].odk == 'D']
        special_drives = [d for d in filtered_drives if d.plays and d.plays[0].odk == 'K']
        total_plays = sum(len(d.plays) for d in filtered_drives)
        filtered_plays = [play for drive in filtered_drives for play in drive.plays]

        mapped_play_categories = []
        for p in filtered_plays:
            if p.off_play and p.off_play.strip():
                general_category = play_mapping.get(p.off_play.strip())
                if general_category:
                    mapped_play_categories.append(general_category)

        play_type_counts = Counter(mapped_play_categories)
        
        play_type_labels = list(play_type_counts.keys())
        play_type_values = list(play_type_counts.values())

        pass_count = play_type_counts.get('PASS', 0)
        run_count = play_type_counts.get('RUN', 0)

        result_type_labels = ['PASS', 'RUN']
        result_type_values = [pass_count, run_count]

        penalty_plays = [p for p in filtered_plays if p.result == 'Penalty']        
        penalty_counter = Counter(p.penalty_type for p in penalty_plays if p.penalty_type)
        penalty_labels = list(penalty_counter.keys())
        penalty_values = list(penalty_counter.values())

        return render_template("game/dashboard.html", game=game, odk_filter=odk_filter,
            filtered_drives=filtered_drives,
            offense_drives=offense_drives, defense_drives=defense_drives,
            special_drives=special_drives, total_plays=total_plays,
            play_type_labels=play_type_labels,
            play_type_values=play_type_values,
            result_type_labels=result_type_labels,
            result_type_values=result_type_values,
            penalty_labels=penalty_labels,
            penalty_values=penalty_values)
    
    @login_required
    def game_options(self) -> str:
        # filter away team
        teams = TeamModel.query.all()
        games = GameModel.query.all()
        return render_template(
            template_name_or_list='game/game_options.html',
            games=games,
            teams=teams
        )

    @login_required
    def filter_drives(self):
        selected_odk = request.args.get('Odk')
        game_id = request.args.get('Id')
        game = GameModel.get_by_id(game_id)
        if selected_odk:
            game.drives = [drive for drive in game.drives
                            if drive.plays and drive.plays[0].odk == selected_odk]
            return render_template("game/partials/_drive_rows.html", game=game)
        else:
            return render_template("game/partials/_drive_rows.html", game=game)

    @login_required
    def game_detail(self, game_id: int) -> str:
        game = GameModel.get_by_id(game_id)
        for drive in game.drives:
            if len(drive.plays) > 0:
                print(drive.plays[0].odk)
        return render_template(template_name_or_list='game/game_detail.html', game=game)

    @login_required
    def add_game(self) -> str | Response:
        if request.method == 'POST':
            try:
                data = request.form
                game_name = data.get('game_name')
                game_date = data.get('date')
                game_time = data.get('time')
                try:
                    home_team_id = int(data.get('home_team_id'))
                    away_team_id = int(data.get('away_team_id'))
                except ValueError:
                    flash(message='Please enter a valid team ID.', category='warning')
                    return redirect(request.url)

                if any([not game_name, not game_date, not game_time, not home_team_id, not away_team_id]):
                    flash(message="Something weird happened. Please try again later.", category='danger')
                    return redirect(request.url)

                if home_team_id == away_team_id:
                    flash(message="Home and Away teams must be different.", category="warning")
                    return redirect(request.url)

                home_check = TeamModel.query.get(home_team_id)
                away_check = TeamModel.query.get(away_team_id)

                if not home_check or not away_check:
                    flash(message="An error occurred while adding a new game. Please try again.", category='danger')
                    return redirect(request.url)

                game = GameModel(
                    name=game_name,
                    game_date=datetime.strptime(game_date, "%Y-%m-%d"),
                    game_time=game_time,
                    home_team_id=home_team_id,
                    away_team_id=away_team_id
                )

                db.session.add(game)
                db.session.commit()
                flash(message='Game added successfully!', category='success')
                return redirect(url_for('game_options'))
            except Exception as e:
                db.session.rollback()
                flash(message="An error occurred while adding a new game. Please try again.", category='danger')
                print(f"[{type(e).__name__}] Failed to add game: {e}")

        # GET Handler
        teams = TeamModel.query.all()
        return render_template(template_name_or_list='game/add_game.html', teams=teams)

    @login_required
    def delete_game(self, game_id: int) -> Response:
        try:
            game = GameModel.get_by_id(game_id)
            db.session.delete(game)
            db.session.commit()
            flash(message='Game deleted successfully', category='success')
        except Exception as e:
            db.session.rollback()
            flash(message="An error occurred while deleting the game. Please try again.", category='danger')
            print(f"[{type(e).__name__}] Failed to delete game: {e}")
        return redirect(url_for('game_options'))

    @login_required
    def add_drive(self, game_id):
        try:
            drive = DriveModel(game_id=game_id)
            db.session.add(drive)
            db.session.commit()
            flash(message='Drive added successfully!', category='success')
        except Exception as e:
            db.session.rollback()
            flash(message="An error occurred while adding the drive. Please try again.", category='danger')
            print(f"[{type(e).__name__}] Failed to add drive: {e}")
        return redirect(url_for(endpoint='game_detail', game_id=game_id))

    @staticmethod
    def convert(yard_line: int) -> int:
        """converts yard-field values to format 0-100"""
        if yard_line == 50:
            return 50
        if yard_line < 0:
            return -yard_line
        return 100 - yard_line

    @login_required
    def drive_play_chart(self, game_id, drive_id):
        game = GameModel.get_by_id(game_id)
        drive = DriveModel.query.filter_by(game_id=game_id, id=drive_id).first_or_404()
        plays = PlayModel.query.filter_by(drive_id=drive.id).order_by(PlayModel.id).all()

        plays_data = []
        
        home_team = game.home_team
        away_team = game.away_team
        home_team_color = home_team.primary_color if home_team else "#010748"
        away_team_color = away_team.primary_color if home_team else "#010748"
        home_team_text_color = get_readable_text_color(home_team_color) if home_team else "#FFFFFF"
        away_team_text_color = get_readable_text_color(away_team_color) if home_team else "#FFFFFF"
        
        for play in plays:

            raw_start = play.yard_line
            raw_end = play.yard_line
            start_yard = self.convert(raw_start)
            end_yard = self.convert(raw_end) + play.gain_loss

            start_yard = max(0, min(100, start_yard))
            end_yard = max(0, min(100, end_yard))

            loss_detected = (play.gain_loss or 0) < 0
            if loss_detected:
                temp = start_yard
                start_yard = end_yard
                end_yard = temp

            plays_data.append({
                'id': play.id,
                'start': start_yard,
                'end': end_yard,
                'yards': play.gain_loss or 0,
                'result': play.result or 'Unknown',
                'play_count': len(plays),
                'loss': loss_detected
            })

        return render_template(
            template_name_or_list='drive/drive_play_chart.html',
            game=game,
            drive=drive,
            plays=plays_data,
            max=max,
            home = home_team_color,
            away = away_team_color,
            home_text = home_team_text_color,
            away_text = away_team_text_color
        )

    @login_required
    def drive_chart(self, game_id):
        game = GameModel.get_by_id(game_id)
        drives = DriveModel.query.filter_by(game_id=game_id).all()

        drives_data = []
        
        home_team = game.home_team
        away_team = game.away_team
        home_team_color = home_team.primary_color if home_team else "#010748"
        away_team_color = away_team.primary_color if home_team else "#010748"
        home_team_text_color = get_readable_text_color(home_team_color) if home_team else "#FFFFFF"
        away_team_text_color = get_readable_text_color(away_team_color) if home_team else "#FFFFFF"
            
        for drive in drives:
            plays = PlayModel.query.filter_by(drive_id=drive.id).order_by(PlayModel.id).all()
            number_plays = len(plays)

            if number_plays == 0 or not plays:
                continue  # if no play in a drive, continue with the next

            raw_start = plays[0].yard_line
            raw_end = plays[-1].yard_line
            start_yard = self.convert(raw_start)
            end_yard = self.convert(raw_end) + plays[-1].gain_loss

            if drive.result and drive.result.lower() == 'touchdown': end_yard = 100

            start_yard = max(0, min(100, start_yard))
            end_yard = max(0, min(100, end_yard))

            loss_detected = end_yard < start_yard
            if loss_detected:
                temp = start_yard
                start_yard = end_yard
                end_yard = temp
                
            drives_data.append({
                'id': drive.id,
                'team': game.name.split(' vs ')[0],
                'start': start_yard,
                'end': end_yard,
                'result': drive.result or 'Unknown',
                'play_count': len(plays),
                'loss': loss_detected
            })
        return render_template(
            template_name_or_list='drive/drive_chart.html',
            game=game,
            drives=drives_data,
            max=max,
            home = home_team_color,
            away = away_team_color,
            home_text = home_team_text_color,
            away_text = away_team_text_color
        )

    @login_required
    def export_game(self, game_id):
        game = GameModel.get_by_id(game_id)
        drives = DriveModel.query.filter_by(game_id=game.id).order_by(DriveModel.id).all()

        csv_data = io.StringIO()
        writer = csv.writer(csv_data, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([
            'Drive #', 'Play #', 'ODK', 'Quarter', 'Down', 'Distance', 'Yard Line', 'Play Type', 'Result',
            'Gain/Loss', 'Personnel', 'Formation', 'Strength', 'Adjustment', 'Motion', 'Protection',
            'Play Call', 'Direction', 'Tag', 'Hash'
        ])

        for drive_index, drive in enumerate(drives, start=1):
            plays = PlayModel.query.filter_by(drive_id=drive.id).order_by(PlayModel.id).all()
            for play_index, play in enumerate(plays, start=1):
                writer.writerow([
                    drive_index, play_index, play.odk, play.quarter, play.down, play.distance, play.yard_line,
                    play.play_type, play.result, play.gain_loss, play.personnel, play.off_form,
                    play.form_str, play.form_adj, play.motion, play.protection, play.off_play,
                    play.dir_call, play.tag, play.hash
                ])

        response = make_response(csv_data.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=game_{game.id}_drives.csv'
        response.headers['Content-type'] = 'text/csv'

        return response

def get_readable_text_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    return "#000000" if brightness > 186 else "#ffffff"