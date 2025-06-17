import csv
from datetime import datetime
import io
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, Response
from flask_login import login_required
from app.extensions import db
from app.models.drive import DriveModel
from app.models.game import GameModel
from app.models.play import PlayModel


class GameController:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule(rule='/game-options', view_func=self.game_options)
        self.app.add_url_rule(rule='/game/<int:game_id>', view_func=self.game_detail)
        self.app.add_url_rule(rule='/add-game', view_func=self.add_game, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/game/<int:game_id>/delete', view_func=self.delete_game, methods=['POST'])
        self.app.add_url_rule(rule='/game/<int:game_id>/add-drive', view_func=self.add_drive, methods=['POST'])
        self.app.add_url_rule(rule='/game/<int:game_id>/drive-chart', view_func=self.drive_chart)
        self.app.add_url_rule(rule='/game/<int:game_id>/export', view_func=self.export_game)

    @login_required
    def game_options(self) -> str:
        games = GameModel.query.all()
        return render_template('game/game_options.html', games=games)

    @login_required
    def game_detail(self, game_id: int) -> str:
        game = GameModel.query.get_or_404(game_id)
        return render_template('game/game_detail.html', game=game)

    @login_required
    def add_game(self) -> str | Response:
        if request.method == 'POST':
            try:
                game = GameModel(
                    game_name=request.form.get('game_name'),
                    date=datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
                    time=request.form.get('time')
                )
                db.session.add(game)
                db.session.commit()
                flash('Game added successfully!', 'success')
                return redirect(url_for('game_options'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding game: {str(e)}', 'error')
        return render_template('game/add_game.html')

    @login_required
    def delete_game(self, game_id: int) -> Response:
        try:
            game = GameModel.query.get_or_404(game_id)
            db.session.delete(game)
            db.session.commit()
            flash('Game deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting game: {str(e)}', 'error')
        return redirect(url_for('game_options'))

    @login_required
    def add_drive(self, game_id):
        try:
            drive = DriveModel(game_id=game_id)
            db.session.add(drive)
            db.session.commit()
            flash('Drive added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding drive: {str(e)}', 'error')
        return redirect(url_for('game_detail', game_id=game_id))

    @login_required
    def drive_chart(self, game_id):
        game = GameModel.query.get_or_404(game_id)
        drives = DriveModel.query.filter_by(game_id=game_id).all()

        drives_data = []
        for drive in drives:
            plays = PlayModel.query.filter_by(drive_id=drive.id).order_by(PlayModel.id).all()
            number_plays = len(plays)

            # todo: enhance method to display a nice view when no plays for a drive
            if number_plays == 0 or not plays:
                drives_data.append({
                    'id': drive.id,
                    'team': game.game_name.split(' vs ')[0],
                    'start': 0,
                    'end': 0,
                    'result': drive.result or 'Unknown',
                    'play_count': len(plays),
                    'loss': False
                })
                return render_template('drive/drive_chart.html', game=game, drives=drives_data, max=max)

            start_yard = plays[0].yard_line
            end_yard = plays[number_plays - 1].yard_line
            if start_yard < 0:
                start_yard = start_yard * (-1)
                print(start_yard)
            else:
                start_yard = start_yard + 50
            if end_yard < 0:
                end_yard = end_yard * (-1)
                print(end_yard)
            if end_yard != 50 and end_yard > 0:
                end_yard = end_yard

            if drive.result and drive.result.lower() == 'touchdown':
                end_yard = 100

            start_yard = max(0, min(100, start_yard))
            end_yard = max(0, min(100, end_yard))

            loss_detected = end_yard < start_yard
            if loss_detected:
                temp = start_yard
                start_yard = end_yard
                end_yard = temp

            drives_data.append({
                'id': drive.id,
                'team': game.game_name.split(' vs ')[0],
                'start': start_yard,
                'end': end_yard,
                'result': drive.result or 'Unknown',
                'play_count': len(plays),
                'loss': loss_detected
            })
        print(f"Drives Data: {drives_data}")
        return render_template('drive/drive_chart.html', game=game, drives=drives_data, max=max)

    @login_required
    def export_game(self, game_id):
        game = GameModel.query.get_or_404(game_id)
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
