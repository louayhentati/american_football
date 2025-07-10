import csv
import io

from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from app.extensions import db
from app.models.drive import DriveModel
from app.models.play import PlayModel
from app.models.play_call import PlayCallModel
from app.models.play_option import PlayOptionModel
from app.penalty_catalogue import PENALTY_RULES


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
            return self._handle_add_play_post_request(drive_id, drive)
        return self._handle_add_play_get_request(drive_id)

    def _handle_add_play_post_request(self, drive_id, drive):
        play = self._create_play_from_form(drive_id)
        db.session.add(play)
        db.session.flush()

        self._update_play_fields(play, drive_id, drive)
        db.session.commit()

        flash('Play added successfully!', 'success')
        return redirect(url_for('drive_detail', drive_id=drive_id))

    def _create_play_from_form(self, drive_id):
        form = request.form
        off_play_value = form.get('off_play')
        play_option = PlayOptionModel.query.filter_by(value=off_play_value).first()
        play_type = play_option.play_call.name if play_option and play_option.play_call else None

        rule = next((r for r in PENALTY_RULES if r["type"] == form.get("penalty_type")), None)
        yard_line = self.convert(int(form.get('yard_line')))
        raw_penalty_spot = self.convert(int(form.get("penalty_spot_yard") or 0))
        foul_team = form.get("foul_team") or None

        if rule:
            if rule.get('spot_foul') and raw_penalty_spot is not None:
                gain_loss = raw_penalty_spot - yard_line
            elif rule.get("yards"):
                if foul_team == "H":
                    gain_loss = -abs(rule["yards"])
                elif foul_team == "O":
                    gain_loss = abs(rule["yards"])
        else:
            gain_loss = int(form.get('gain_loss') or 0)

        return PlayModel(
            drive_id=drive_id,
            odk=form['odk'],
            down=int(form.get('down') or 1),
            distance=int(form.get('distance') or 10),
            yard_line=int(form.get('yard_line') or 25),
            hash=form.get('hash', 'M'),
            personnel=form.get('personnel'),
            off_form=form.get('off_form'),
            form_str=form.get('form_str'),
            form_adj=form.get('form_adj'),
            motion=form.get('motion'),
            protection=form.get('protection'),
            off_play=off_play_value,
            play_type=play_type,
            dir_call=form.get('dir_call'),
            tag=form.get('tag'),
            result=form.get('result'),
            gain_loss=gain_loss,
            penalty_type=form.get("penalty_type", None),
            penalty_spot_yard=form.get("penalty_spot_yard", None),
            foul_team=foul_team,
            play_type1=request.form.get('play_type1'),
            defense_front=request.form.get('defense_front'),
            defense_strongside=request.form.get('defense_strongside'),
            blitz=request.form.get('blitz'),
            slants=request.form.get('slants'),
            coverage=request.form.get('coverage'),
            tackler1=request.form.get('tackler1'),
            tackler2=request.form.get('tackler2'),
            interceptor=request.form.get('interceptor'),
            returner=request.form.get('returner'),
            returner_yard=request.form.get('returner_yard'),
            kicker=request.form.get('kicker'),
            kicker_yard=request.form.get('kicker_yard')
        )

    def _update_play_fields(self, play, drive_id, drive):
        previous_play = self._get_previous_play(drive_id, play.id)
        if not previous_play:
            return

        next_fields = self.__calculate_next_play_fields(last_play=previous_play)
        play.down = next_fields.get('down', play.down)
        play.distance = next_fields.get('distance', play.distance)
        play.yard_line = next_fields.get('yard_line', play.yard_line)

        if next_fields.get('possession_change', False):
            drive.ended = True
        elif play.result in ['Touchdown', 'Rush, TD', 'Complete, TD', 'Interception', 'Interception, Def TD', 'Fumble',
                             'Fumble, Def TD', 'Punt']:
            drive.ended = True

    @staticmethod
    def _get_previous_play(drive_id, current_play_id):
        return (PlayModel.query
                .filter(PlayModel.drive_id == drive_id,
                        PlayModel.id != current_play_id)
                .order_by(PlayModel.id.desc())
                .first())

    def _handle_add_play_get_request(self, drive_id):
        drive = DriveModel.query.get_or_404(drive_id)
        if drive.ended:
            flash(message="This drive has ended. Cannot add more plays!", category="danger")
            return redirect(url_for('drive_detail', drive_id=drive_id))

        play_call_details = self._get_play_call_details()
        options = self._get_add_play_form_options()
        down, distance, yard_line = self._get_default_play_fields(drive_id)

        return render_template(
            template_name_or_list='play/add_play.html',
            drive=drive,
            drive_id=drive_id,
            play=None,
            options=options,
            default_down=down,
            default_distance=distance,
            default_yard_line=yard_line,
            play_call_details=play_call_details
        )

    @staticmethod
    def _get_play_call_details():
        off_play_name = request.args.get('off_play') or None
        if not off_play_name:
            return {}

        play_call = PlayOptionModel.query.filter_by(value=off_play_name).first()
        return {'id': play_call.id, 'name': play_call.name} if play_call else {}

    def _get_add_play_form_options(self):
        options = {}
        defense_parameters = [
            'play_type1','defense_front', 'defense_strongside',
            'blitz', 'slants', 'coverage'
        ]
        for param in self.play_parameters:
            entries = PlayOptionModel.query.filter_by(parameter_name=param, enabled=True).all()

            if param == 'off_play':
                enriched = []
                for entry in entries:
                    play_call = PlayCallModel.query.get(entry.play_call_id)
                    label = f"{entry.value} ({play_call.name})" if play_call else entry.value
                    enriched.append({
                        'id': entry.id,
                        'value': entry.value,
                        'label': label,
                        'play_call_id': entry.play_call_id
                    })

                options[param] = enriched
            else:
                options[param] = [
                    {'id': entry.id, 'value': entry.value, 'label': entry.value}
                    for entry in entries
                ]
        options['penalty_type'] = [{'value': r['type'], 'label': r['type']}
                                   for r in PENALTY_RULES
                                   ]
        # Add defense parameters
        for param in defense_parameters:
            entries = PlayOptionModel.query.filter_by(parameter_name=param, enabled=True).all()
            options[param] = [
                {'id': entry.id, 'value': entry.value, 'label': entry.value}
                for entry in entries
            ]
        return options

    def _get_default_play_fields(self, drive_id):
        last_play = (
            PlayModel.query
            .filter_by(drive_id=drive_id)
            .order_by(PlayModel.id.desc())
            .first()
        )

        if not last_play:
            return 1, 10, -25

        next_fields = self.__calculate_next_play_fields(last_play)
        return (
            next_fields.get('down', 1),
            next_fields.get('distance', 10),
            next_fields.get('yard_line', 25)
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
        game_id = None
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

    # Function for converting yard-field values to format 0-100
    @staticmethod
    def convert(yard_line: int) -> int:
        if yard_line < 0:
            return -yard_line
        if yard_line == 50:
            return 50
        return 100 - yard_line

    # Function for converting back to yard-field values
    @staticmethod
    def convert_back(yard_line: int) -> int:
        if yard_line < 50:
            return -yard_line
        if yard_line == 50:
            return 50
        return 100 - yard_line

    def __calculate_next_play_fields(self, last_play):
        gained = last_play.gain_loss if hasattr(last_play, 'gain_loss') else last_play['gain_loss']
        down = last_play.down if hasattr(last_play, 'down') else last_play['down']
        distance = last_play.distance if hasattr(last_play, 'distance') else last_play['distance']
        yard_line = last_play.yard_line if hasattr(last_play, 'yard_line') else last_play['yard_line']
        result = last_play.result if hasattr(last_play, 'result') else last_play['result']
        penalty_type = last_play.penalty_type if hasattr(last_play, 'penalty_type') else last_play["penalty_type"]
        turnover_results = [
            'Interception', 'Interception, Def TD',
            'Fumble', 'Fumble, Def TD',
            'Punt', 'Sack',
            'Touchdown', 'Rush, TD', 'Complete, TD'
        ]
        possession_change = False
        next_down = 1
        next_distance = 10

        raw_yard_line = self.convert(yard_line) + gained
        new_yard_line = self.convert_back(raw_yard_line)

        if result in turnover_results:
            possession_change = True
            next_down = 1
            next_distance = 10

        elif gained >= distance:
            next_down = 1
            next_distance = 10

        elif down == 4:
            possession_change = True
            next_down = 1
            next_distance = 10

        elif result == "Penalty" and penalty_type:
            rule = next((r for r in PENALTY_RULES if r["type"] == penalty_type), None)
            if rule:
                if rule.get("automatic_first_down"):  # Wenn die Regel automatic first down beinhaltet
                    next_down = 1
                    next_distance = 10

                elif rule.get("loss_of_down"):  # Wenn die Regel loss of down beinhaltet
                    next_down = down + 1
                    next_distance = 10
        else:
            next_down = down + 1
            next_distance = distance - gained

        return {
            "possession_change": possession_change,
            "down": next_down,
            "distance": next_distance,
            "yard_line": new_yard_line
        }
