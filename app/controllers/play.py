from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.drive import DriveModel
from app.models.play import PlayModel
from app.models.play_call import PlayCallModel
from app.models.play_option import PlayOptionModel


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
        print(f'off_play_value: {off_play_value}')

        play_option = PlayOptionModel.query.filter_by(value=off_play_value).first()
        print(f'play_option: {play_option}')
        play_type = play_option.play_call.name if play_option and play_option.play_call else None
        print(f'play_type: {play_type}')

        options = self._get_add_play_form_options()
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
            turnover_results = [
                'Interception', 'Interception, Def TD',
                'Fumble', 'Fumble, Def TD',
                'Punt', 'Sack',
                'Touchdown', 'Rush, TD', 'Complete, TD'
            ]

            if (last_play.result in turnover_results or
                    (last_play.down == 4 and last_play.gain_loss < last_play.distance)):
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

        return options
