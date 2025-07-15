from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.drive import DriveModel
from app.models.play import PlayModel
from app.models.play_call import PlayCallModel
from app.models.play_option import PlayOptionModel
from app.penalty_catalogue import PENALTY_RULES
from app.penalty_catalogue import SPOT_FOULS
from app.config import ApplicationData


class PlayController:
    def __init__(self, app: Flask, play_parameters: dict) -> None:
        self.app = app
        self.play_parameters = play_parameters
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule(rule='/play/<int:play_id>/edit', view_func=self.edit_play, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/play/<int:play_id>/delete', view_func=self.delete_play, methods=['POST'])

    @login_required
    def edit_play(self, play_id):
        form = request.form
        off_play_value = form.get('off_play')
        play_option = PlayOptionModel.query.filter_by(value=off_play_value).first()
        play_type = play_option.play_call.name if play_option and play_option.play_call else None

        options = self._get_add_play_form_options()
        options['penalty_type'] = [
            {'value': r['type'], 'label': r['type']}
            for r in PENALTY_RULES
        ]
        play = PlayModel.query.get_or_404(play_id)

        if request.method == 'POST':
            try:
                result_form = request.form.get('result')
                play.odk = request.form.get('odk')
                play.quarter = request.form.get('quarter', type=int)
                play.yard_line = request.form.get('yard_line', type=int)
                play.down = request.form.get('down', type=int)
                play.distance = request.form.get('distance', type=int)
                # play.play_type = request.form.get('play_type')
                play.play_type = play_type
                play.result = result_form
                play.gain_loss = request.form.get('gain_loss', type=int)
                play.personnel = request.form.get('personnel')
                play.off_form = request.form.get('off_form')
                play.form_str = request.form.get('form_str')
                play.form_adj = request.form.get('form_adj')
                play.motion = request.form.get('motion')
                play.protection = request.form.get('protection')
                play.off_play = request.form.get('off_play')
                play.dir_call = request.form.get('dir_call')
                play.tag = request.form.get('tag')
                play.hash = request.form.get('hash')
                # extra für rusher,passe,receiver
                play.rusher_number = request.form.get('rusher_number', type=int)
                play.passer = request.form.get('passer', type=int)
                play.receiver = request.form.get('receiver', type=int)
                # extra für Deffense in add play
                play.play_type1 = request.form.get('play_type1')
                play.defense_front = request.form.get('defense_front')
                play.defense_strongside = request.form.get('defense_strongside')
                play.blitz = request.form.get('blitz')
                play.slants = request.form.get('slants')
                play.coverage = request.form.get('coverage')
                play.tackler1 = request.form.get('tackler1', type=int)
                play.tackler2 = request.form.get('tackler2', type=int)
                play.interceptor = request.form.get('interceptor', type=int)
                # extra für special team  in add play
                play.returner = request.form.get('returner', type=int)
                play.returner_yard = request.form.get('returner_yard', type=int)
                play.kicker = request.form.get('kicker', type=int)
                play.kicker_yard = request.form.get('kicker_yard', type=int)
                print(SPOT_FOULS)
                if play.result == "Penalty":
                    play.penalty_type  = request.form.get('penalty_type') or None
                    play.foul_team = request.form.get('foul_team') or None  
                    if play.penalty_type in SPOT_FOULS:
                        play.penalty_spot_yard = int(request.form.get('penalty_spot_yard') or 0 )
                    else:
                        play.penalty_spot_yard = None   
                else:
                    play.foul_team = None
                    play.penalty_type = None
                    play.penalty_spot_yard = None

                rule = None
                if play.result == "Penalty" and play.penalty_type:
                    rule = next((r for r in PENALTY_RULES if r["type"] == play.penalty_type), None)
                    if rule:  
                        if play.penalty_spot_yard not in [None, 0]:
                            yard_line = convert(play.yard_line) 
                            raw_penalty_spot = convert(play.penalty_spot_yard)
                            if rule.get('spot_foul') and raw_penalty_spot is not None:
                                if play.foul_team == "H":
                                    play.gain_loss = raw_penalty_spot - abs(rule["yards"]) - yard_line
                                elif play.foul_team == "O":
                                    play.gain_loss = raw_penalty_spot + abs(rule["yards"]) - yard_line
                                
                        elif rule.get("yards") and play.foul_team == "H":
                            play.gain_loss = -abs(rule["yards"])
                            play.penalty_spot_yard = None
                            
                        else: 
                            play.gain_loss = abs(rule["yards"])
                            play.penalty_spot_yard = None
                            
                else: # Wenn kein Penalty, nimm Wert aus dem Formular
                    play.gain_loss = request.form.get('gain_loss') or 0
                    
                
                drive = DriveModel.query.get_or_404(play.drive_id)
                drive.result = result_form if result_form else "In Progress"

                db.session.commit()

                drive = DriveModel.query.get_or_404(play.drive_id)
                self._recalculate_drive_ended(drive)
                flash('Play updated successfully!', 'success')
                return redirect(url_for('drive_detail', drive_id=play.drive_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating play: {str(e)}', 'error')

        return render_template('play/add_play.html',
                               play=play,
                               options=options,
                               drive_id=play.drive_id)

    @login_required
    def _recalculate_drive_ended(self, drive):
        last_play = (
            PlayModel.query
            .filter_by(drive_id=drive.id)
            .order_by(PlayModel.id.desc())
            .first()
        )

        if not last_play:
            drive.ended = False
        else:
            if (last_play.result in ApplicationData.DRIVE_ENDING_RESULTS or
                    (last_play.down == 4 and last_play.gain_loss < last_play.distance)
            ):
                drive.ended = True
            else:
                drive.ended = False
        db.session.commit()

    @login_required
    def delete_play(self, play_id):
        try:
            play = PlayModel.query.get_or_404(play_id)
            drive_id = play.drive_id
            db.session.delete(play)
            db.session.commit()
            flash('Play deleted successfully', 'success')

            drive = DriveModel.query.get_or_404(drive_id)

            last_play = (
                PlayModel.query
                .filter_by(drive_id=drive_id)
                .order_by(PlayModel.id.desc())
                .first()
            )
            drive.result = last_play.result if last_play and last_play.result else "In Progress"
            self._recalculate_drive_ended(drive)

        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting play: {str(e)}', 'error')
        return redirect(url_for('drive_detail', drive_id=drive_id))

    # redundant : same as in controllers/drive.py
    # refactoring -> later
    def _get_add_play_form_options(self):
        options = {}

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
                        'label': label
                    })
                options[param] = enriched
            else:
                options[param] = [
                    {'id': entry.id, 'value': entry.value, 'label': entry.value}
                    for entry in entries
                ]
        defense_params = [
            'play_type1','defense_front', 'defense_strongside',
            'blitz', 'slants', 'coverage'
        ]

        for param in defense_params:
            if param not in options:
                entries = PlayOptionModel.query.filter_by(
                    parameter_name=param,
                    enabled=True
                ).all()
                options[param] = [
                    {'id': entry.id, 'value': entry.value, 'label': entry.value}
                    for entry in entries
                ]

        return options


def convert(yl: int) -> int:
    if yl < 0: return -yl
    if yl == 50: return 50
    return 100 - yl
