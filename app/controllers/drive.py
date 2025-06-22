import csv
import io

from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from app.extensions import db
from app.models.drive import DriveModel
from app.models.play import PlayModel
from app.models.play_option import PlayOptionModel


class DriveController:
    def __init__(self, app: Flask, play_parameters: dict) -> None:
        self.app = app
        self.play_parameters = play_parameters
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule(rule='/drives/<int:drive_id>/add_play', view_func=self.add_play, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/drive/<int:drive_id>', view_func=self.drive_detail)
        self.app.add_url_rule(rule='/drive/<int:drive_id>/delete', view_func=self.delete_drive, methods=['POST'])
        self.app.add_url_rule(rule='/drive/<int:drive_id>/export', view_func=self.export_drive, methods=['GET'])

    @login_required
    def add_play(self, drive_id):

        drive = DriveModel.query.get_or_404(drive_id)

        if request.method == 'POST':

            play = PlayModel(
                drive_id=drive_id,
                odk=request.form['odk'],
                down=int(request.form.get('down') or 1),
                distance=int(request.form.get('distance') or 10),
                yard_line=int(request.form.get('yard_line') or 25),
                hash=request.form.get('hash', 'M'),
                personnel=request.form.get('personnel'),
                off_form=request.form.get('off_form'),
                form_str=request.form.get('form_str'),
                form_adj=request.form.get('form_adj'),
                motion=request.form.get('motion'),
                protection=request.form.get('protection'),
                off_play=request.form.get('off_play'),
                dir_call=request.form.get('dir_call'),
                tag=request.form.get('tag'),
                play_type=request.form.get('play_type'),
                result=request.form.get('result'),
                gain_loss=int(request.form.get('gain_loss') or 0)
            )

            db.session.add(play)
            db.session.flush()

            previous_play = (
                PlayModel.query
                .filter(PlayModel.drive_id == drive_id, PlayModel.id != play.id)
                .order_by(PlayModel.id.desc())
                .first()
            )

            if previous_play:
                next_fields = self.__calculate_next_play_fields(last_play=previous_play)

                play.down = next_fields.get('down', play.down)
                play.distance = next_fields.get('distance', play.distance)
                play.yard_line = next_fields.get('yard_line', play.yard_line)

                if next_fields.get('possession_change', False):
                    drive.ended = True

            db.session.commit()

            flash('Play added successfully!', 'success')
            return redirect(url_for('drive_detail', drive_id=drive_id))

        options = {}
        for param in self.play_parameters:
            options[param] = PlayOptionModel.query.filter_by(parameter_name=param, enabled=True).all()

        last_play = (
            PlayModel.query
            .filter_by(drive_id=drive_id)
            .order_by(PlayModel.id.desc())
            .first()
        )
        print(f'last_play: {last_play}')

        default_down = 1
        default_distance = 10
        default_yard_line = 25  # <- default starting position

        if last_play:
            next_fields = self.__calculate_next_play_fields(last_play)
            default_down = next_fields.get('down', default_down)
            default_distance = next_fields.get('distance', default_distance)
            default_yard_line = next_fields.get('yard_line', default_yard_line)
            print(f'add_play : default_yard_line = {default_yard_line}')

        return render_template(
            template_name_or_list='play/add_play.html',
            drive_id=drive_id,
            play=None,
            options=options,
            default_down=default_down,
            default_distance=default_distance,
            default_yard_line=default_yard_line
        )

    @login_required
    def drive_detail(self, drive_id):
        drive = DriveModel.query.get_or_404(drive_id)
        for play in drive.plays:
            # Here we replace the 'None' with '-'
            for column in play.__table__.columns:
                if getattr(play, column.name) is None:
                    setattr(play, column.name, '-')
        return render_template('drive/drive_detail.html', drive=drive)

    @login_required
    def delete_drive(self, drive_id):
        try:
            drive = DriveModel.query.get_or_404(drive_id)
            game_id = drive.game_id
            db.session.delete(drive)
            db.session.commit()
            flash('Drive deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting drive: {str(e)}', 'error')
        return redirect(url_for('game_detail', game_id=game_id))

    @login_required
    def export_drive(self, drive_id):
        drive = DriveModel.query.get_or_404(drive_id)
        plays = PlayModel.query.filter_by(drive_id=drive.id).order_by(PlayModel.id).all()

        csv_data = io.StringIO()
        writer = csv.writer(csv_data)
        writer.writerow([
            'Play #', 'ODK', 'Quarter', 'Down', 'Distance', 'Yard Line', 'Play Type', 'Result',
            'Gain/Loss', 'Personnel', 'Formation', 'Strength', 'Adjustment', 'Motion', 'Protection',
            'Play Call', 'Direction', 'Tag', 'Hash'
        ])

        for index_, play in enumerate(plays, start=1):
            writer.writerow([
                index_, play.odk, play.quarter, play.down, play.distance, play.yard_line,
                play.play_type, play.result, play.gain_loss, play.personnel, play.off_form,
                play.form_str, play.form_adj, play.motion, play.protection, play.off_play,
                play.dir_call, play.tag, play.hash
            ])

        response = make_response(csv_data.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=drive_{drive.id}.csv'
        response.headers['Content-type'] = 'text/csv'

        return response

    @staticmethod
    def __calculate_next_play_fields(last_play):
        gained = last_play.gain_loss if hasattr(last_play, 'gain_loss') else last_play['gain_loss']
        down = last_play.down if hasattr(last_play, 'down') else last_play['down']
        distance = last_play.distance if hasattr(last_play, 'distance') else last_play['distance']
        yard_line = last_play.yard_line if hasattr(last_play, 'yard_line') else last_play['yard_line']

        turnover_results = [
            'Interception', 'Interception, Def TD',
            'Fumble', 'Fumble, Def TD',
            'Punt', 'Sack',
            'Touchdown', 'Rush, TD', 'Complete, TD'
        ]

        result = last_play.result if hasattr(last_play, 'result') else last_play.get('result')

        if result in turnover_results:
            return {
                'possession_change': True,
                'down': 1,
                'distance': 10,
                'yard_line': 100 - (yard_line + gained)
            }

        new_yard_line = yard_line + gained

        if gained >= distance:
            return {
                'down': 1,
                'distance': 10,
                'yard_line': new_yard_line
            }

        if down == 4:
            return {
                'possession_change': True,
                'down': 1,
                'distance': 10,
                'yard_line': 100 - new_yard_line
            }

        return {
            'down': down + 1,
            'distance': distance - gained,
            'yard_line': new_yard_line
        }
