import csv
import io

from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from app.extensions import db
from app.models.drive import DriveModel
from app.models.play import PlayModel
from app.models.play_call import PlayCallModel
from app.models.play_option import PlayOptionModel


class DriveController:
    def __init__(self, app: Flask, play_parameters: dict) -> None:
        self.app = app
        self.play_parameters = play_parameters
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule('/drive/<int:drive_id>/add_play', view_func=self.add_play, methods=['GET', 'POST'])
        self.app.add_url_rule('/drive/<int:drive_id>', view_func=self.drive_detail)
        self.app.add_url_rule('/drive/<int:drive_id>/delete', view_func=self.delete_drive, methods=['POST'])
        self.app.add_url_rule('/drive/<int:drive_id>/export', view_func=self.export_drive, methods=['GET'])

    @login_required
    def add_play(self, drive_id):
        drive = DriveModel.query.get_or_404(drive_id)

        # Check if drive has ended
        if self._has_drive_ended(drive_id):
            flash("This drive has ended. Cannot add more plays.", "danger")
            return redirect(url_for('drive_detail', drive_id=drive_id))

        if request.method == 'POST':
            return self._handle_add_play_post_request(drive_id, drive)
        return self._handle_add_play_get_request(drive_id, drive)

    def _handle_add_play_post_request(self, drive_id, drive):
        # Validate inputs
        try:
            yard_line = int(request.form.get('yard_line', 25))
            distance = int(request.form.get('distance', 10))
            gain_loss = int(request.form.get('gain_loss', 0))
        except ValueError:
            flash("Invalid numeric input", "danger")
            return redirect(url_for('add_play', drive_id=drive_id))

        # NFL validation rules
        if not (-49 <= yard_line <= 49):
            flash("Yard line must be between -49 (opponent) and 49 (own)", "danger")
            return redirect(url_for('add_play', drive_id=drive_id))
        if not (1 <= distance <= 99):
            flash("Distance must be between 1 and 99 yards", "danger")
            return redirect(url_for('add_play', drive_id=drive_id))
        if not (-99 <= gain_loss <= 99):
            flash("Gain/Loss must be between -99 and 99 yards", "danger")
            return redirect(url_for('add_play', drive_id=drive_id))

        # Create and save play
        play = self._create_play_from_form(drive_id)
        db.session.add(play)
        db.session.commit()
        flash('Play added successfully!', 'success')
        return redirect(url_for('drive_detail', drive_id=drive_id))

    @staticmethod
    def _create_play_from_form(drive_id):
        form = request.form
        off_play_value = form.get('off_play')
        play_option = PlayOptionModel.query.filter_by(value=off_play_value).first()
        play_type = play_option.play_call.name if play_option and play_option.play_call else None

        # safely converts numeric fields with defaults
        def to_int(val, default):
            try:
                return int(val)
            except (ValueError, TypeError):
                return default

        return PlayModel(
            drive_id=drive_id,
            odk=form.get('odk', 'O'),
            down=to_int(form.get('down'), 1),
            distance=to_int(form.get('distance'), 10),
            yard_line=to_int(form.get('yard_line'), 25),
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
            gain_loss=to_int(form.get('gain_loss'), 0)
        )

    def _handle_add_play_get_request(self, drive_id, drive):
        # Get default values based on previous play or NFL defaults
        down, distance, yard_line = self._get_default_play_fields(drive_id)
        options = self._get_add_play_form_options()

        return render_template(
            'play/add_play.html',
            drive_id=drive_id,
            drive=drive,
            play=None,
            options=options,
            default_down=down,
            default_distance=distance,
            default_yard_line=yard_line
        )

    def _get_default_play_fields(self, drive_id):
        """Get next play defaults based on previous play or NFL rules"""
        last_play = PlayModel.query.filter_by(drive_id=drive_id) \
            .order_by(PlayModel.id.desc()).first()

        # NFL defaults for new drive
        if not last_play:
            return 1, 10, 25  # down, distance, yard_line

        # Calculate next play based on NFL rules
        return self._calculate_next_play_fields(last_play)

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
                        'label': label,
                        'play_call_id': entry.play_call_id
                    })

                options[param] = enriched
            else:
                options[param] = [{'id': e.id, 'value': e.value, 'label': e.value} for e in entries]

        return options

    @login_required
    def drive_detail(self, drive_id):
        drive = DriveModel.query.get_or_404(drive_id)
        for play in drive.plays:
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
            flash("An unexpected error occurred while deleting the drive. Please try again.", 'danger')
            print(f"[{type(e).__name__}] Error deleting drive: {e}")
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
            # Handle missing attribute quarter gracefully
            quarter = getattr(play, 'quarter', '-')
            writer.writerow([
                index_, play.odk, quarter, play.down, play.distance, play.yard_line,
                play.play_type, play.result, play.gain_loss, play.personnel, play.off_form,
                play.form_str, play.form_adj, play.motion, play.protection, play.off_play,
                play.dir_call, play.tag, play.hash
            ])

        response = make_response(csv_data.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=drive_{drive.id}.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    @staticmethod
    def _calculate_next_play_fields(last_play):
        """Calculate next play state based on NFL rules"""
        gained = last_play.gain_loss
        down = last_play.down
        distance = last_play.distance
        yard_line = last_play.yard_line

        # Calculate new position with midfield crossing handling
        new_yard_line = yard_line - gained

        # Handle midfield crossing and clamping
        if new_yard_line > 49:
            # Crossed opponent's 50 from own territory
            new_yard_line = -(new_yard_line - 50)
        elif new_yard_line < -49:
            # Crossed own 50 from opponent territory
            new_yard_line = -(new_yard_line + 50)

        # Clamp to field boundaries
        new_yard_line = max(-49, min(49, new_yard_line))

        # Successful conversion
        if gained >= distance:
            return 1, 10, new_yard_line

        # Continue drive
        if down < 4:
            return down + 1, distance - gained, new_yard_line

        # Turnover on downs - flip field
        return 1, 10, -new_yard_line

    def _has_drive_ended(self, drive_id):
        """Check if drive has ended by examining plays"""
        last_play = PlayModel.query.filter_by(drive_id=drive_id) \
            .order_by(PlayModel.id.desc()).first()

        if not last_play:
            return False

        return self._does_play_end_drive(last_play)

    def _does_play_end_drive(self, play):
        """Check if play ends drive based on NFL rules"""
        turnover_results = [
            'Interception', 'Interception, Def TD',
            'Fumble', 'Fumble, Def TD',
            'Punt', 'Touchdown', 'Rush, TD', 'Complete, TD'
        ]

        # Turnover results always end drive
        if play.result and play.result in turnover_results:
            return True

        # 4th down failure
        if play.down == 4 and play.gain_loss < play.distance:
            return True

        return False