# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
import random
import os
from models import db, User, Game, Drive, Play, PlayOption
from teams import teams_data
import csv
import io
from flask import make_response

# Flask app configuration
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    # Author: Gaivy, Hamid

    return User.query.get(int(user_id))


# Constants
PLAY_PARAMETERS = {
    'off_form': 'Offensive Formation',
    'form_str': 'Formation Strength',
    'form_adj': 'Formation Adjustment',
    'motion': 'Motion',
    'protection': 'Protection',
    'off_play': 'Off Play',
    'dir_call': 'Directional Call',
    'tag': 'Tags'
}


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    # Author: Gaivy, Hamid

    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    # Author: Gaivy, Hamid

    db.session.rollback()
    return render_template('500.html'), 500


# Database initialization
@app.route('/init-db')
def init_db():
    # Author: Gaivy, Rashed, Yazan

    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
            test_user = User(username="coach", password="pasword123")
            db.session.add(test_user)
            db.session.commit()
            return "Database initialized and test user created successfully!"
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Authentication routes
@app.route('/')
def index():
    # Author: Gaivy, Rashed, Yazan

    if current_user.is_authenticated:
        return redirect(url_for('game_options'))
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Author: Gaivy

    if current_user.is_authenticated:
        return redirect(url_for('game_options'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('game_options'))
        flash('Invalid credentials')
    return render_template('login.html')


@app.context_processor
def inject_teams():
    # Author: Rashed
    return dict(teams=teams_data)

@app.route('/set_team', methods=['POST'])
@login_required
def set_team():
    # Author: Rashed
    chosen_team = request.form.get('team_name')
    if chosen_team in teams_data:
        session['team_name'] = chosen_team
    return redirect(url_for('game_options'))


@app.route('/logout')
@login_required
def logout():
    # Author: Gaivy, Rashed

    logout_user()
    session.pop('team_name', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


# Game routes
@app.route('/game-options')
@login_required
def game_options():
    # Author: Gaivy

    games = Game.query.all()
    return render_template('game_options.html', games=games)


@app.route('/add-game', methods=['GET', 'POST'])
@login_required
def add_game():
    # Author: Gaivy

    if request.method == 'POST':
        try:
            game = Game(
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
    return render_template('add_game.html')


@app.route('/callsheet')
@login_required
def callsheet():
    # Author: Rashed, Yazan

    # Fetch all plays from the database
    plays = Play.query.filter(Play.odk == 'O').all()

    # Aggregate data for the callsheet
    callsheet_data = {}
    for play in plays:
        # Create a unique key for each combination of off_play, off_form, and form_adj
        key = (play.off_play, play.off_form, play.form_adj)

        # Initialize the dictionary for the key if it doesn't exist
        if key not in callsheet_data:
            callsheet_data[key] = {
                'count': 0,  # Count of plays for this combination
                'total_gain_loss': 0,  # Total gain/loss for this combination
            }

        # Update the count and total gain/loss for this combination
        callsheet_data[key]['count'] += 1
        callsheet_data[key]['total_gain_loss'] += play.gain_loss

    # Calculate Percent and Average for each entry
    total_plays = sum(data['count'] for data in callsheet_data.values())  # Total number of plays
    callsheet_entries = []
    for key, data in callsheet_data.items():
        off_play, off_form, form_adj = key  # Unpack the key
        count = data['count']  # Number of plays for this combination
        total = data['total_gain_loss']  # Total gain/loss for this combination

        # Calculate Percent: (count / total_plays) * 100
        percent = (count / total_plays) * 100 if total_plays > 0 else 0

        # Calculate Average: total / count
        average = total / count if count > 0 else 0

        # Append the entry to the callsheet_entries list
        callsheet_entries.append({
            'off_play': off_play,  # Offense Play
            'off_form': off_form,  # Offense Formation
            'form_adj': form_adj,  # Formation Adjustment
            'count': count,  # Number of plays
            'percent': percent,  # Percentage of total plays
            'total': total,  # Total gain/loss
            'average': average,  # Average gain/loss per play
        })

    # Sort the entries by Offense Play for better readability
    callsheet_entries.sort(key=lambda x: x['count'], reverse=True)

    # Render the callsheet template with the calculated data
    return render_template('callsheet.html', callsheet_entries=callsheet_entries)

@app.route('/game/<int:game_id>/game_callsheet')
@login_required
def game_callsheet(game_id):
    # Author: Rashed, Yazan

    # Fetch plays for the specified game by joining with the Drive table
    plays = Play.query.join(Drive).filter(Drive.game_id == game_id, Play.odk == 'O').all()

    # Aggregate data for the callsheet
    callsheet_data = {}
    for play in plays:
        key = (play.off_play, play.off_form, play.form_adj)
        if key not in callsheet_data:
            callsheet_data[key] = {
                'count': 0,
                'total_gain_loss': 0,
            }
        callsheet_data[key]['count'] += 1
        callsheet_data[key]['total_gain_loss'] += play.gain_loss

    total_plays = sum(data['count'] for data in callsheet_data.values())
    callsheet_entries = []
    for key, data in callsheet_data.items():
        off_play, off_form, form_adj = key
        count = data['count']
        total = data['total_gain_loss']
        percent = (count / total_plays) * 100 if total_plays > 0 else 0
        average = total / count if count > 0 else 0

        callsheet_entries.append({
            'off_play': off_play,
            'off_form': off_form,
            'form_adj': form_adj,
            'count': count,
            'percent': percent,
            'total': total,
            'average': average,
        })

    # Sort the entries by play count in descending order
    callsheet_entries.sort(key=lambda x: x['count'], reverse=True)

    return render_template('game_callsheet.html', callsheet_entries=callsheet_entries, game_id=game_id)


@app.route('/game/<int:game_id>')
@login_required
def game_detail(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template('game_detail.html', game=game)


@app.route('/game/<int:game_id>/delete', methods=['POST'])
@login_required
def delete_game(game_id):
    # Author: Gaivy

    try:
        game = Game.query.get_or_404(game_id)
        db.session.delete(game)
        db.session.commit()
        flash('Game deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting game: {str(e)}', 'error')
    return redirect(url_for('game_options'))


# Drive routes
@app.route('/game/<int:game_id>/add-drive', methods=['POST'])
@login_required
def add_drive(game_id):
    # Author: Gaivy

    try:
        drive = Drive(game_id=game_id)
        db.session.add(drive)
        db.session.commit()
        flash('Drive added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding drive: {str(e)}', 'error')
    return redirect(url_for('game_detail', game_id=game_id))


@app.route('/drive/<int:drive_id>')
@login_required
def drive_detail(drive_id):
    # Author: Gaivy

    drive = Drive.query.get_or_404(drive_id)
    return render_template('drive_detail.html', drive=drive)


@app.route('/drive/<int:drive_id>/delete', methods=['POST'])
@login_required
def delete_drive(drive_id):
    # Author: Gaivy

    try:
        drive = Drive.query.get_or_404(drive_id)
        game_id = drive.game_id
        db.session.delete(drive)
        db.session.commit()
        flash('Drive deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting drive: {str(e)}', 'error')
    return redirect(url_for('game_detail', game_id=game_id))


# Play routes
@app.route('/drive/<int:drive_id>/add_play', methods=['GET', 'POST'])
@login_required
def add_play(drive_id):
    # Author: Gaivy, Rashed, Yazan, Hamid, Hamza

    if request.method == 'POST':
        yard_line = request.form.get('yard_line', type=int)
        down = request.form.get('down', type=int)
        distance = request.form.get('distance', type=int)

        if yard_line is None or down is None or distance is None:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('add_play', drive_id=drive_id))
        try:
            result_form = request.form.get('result')
            play = Play(
                drive_id=drive_id,
                odk=request.form.get('odk'),
                quarter=request.form.get('quarter', type=int), # this was missing, needs to be added in the rest of the code
                yard_line=request.form.get('yard_line', type=int),
                down=request.form.get('down', type=int),
                distance=request.form.get('distance', type=int),
                hash=request.form.get('hash'),  # New field
                play_type=request.form.get('play_type'),
                result=result_form,
                gain_loss=request.form.get('gain_loss', type=int),
                personnel=request.form.get('personnel'),
                off_form=request.form.get('off_form'),
                form_str=request.form.get('form_str'),
                form_adj=request.form.get('form_adj'),
                motion=request.form.get('motion'),
                protection=request.form.get('protection'),
                off_play=request.form.get('off_play'),
                dir_call=request.form.get('dir_call'),
                tag=request.form.get('tag')
            )
            db.session.add(play)

            # update the drive result
            drive = Drive.query.get_or_404(drive_id)
            drive.result = result_form if result_form else "In Progress"

            db.session.commit()

            flash('Play added successfully!', 'success')
            return redirect(url_for('add_play', drive_id=drive_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding play: {str(e)}', 'error')

    options = {}
    for param in PLAY_PARAMETERS:
        options[param] = PlayOption.query.filter_by(parameter_name=param, enabled=True).all()

    return render_template('add_play.html', drive_id=drive_id, play=None, options=options)


@app.route('/play/<int:play_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_play(play_id):
    # Author: Gaivy, Rashed, Yazan, Hamid, Hamza

    play = Play.query.get_or_404(play_id)
    if request.method == 'POST':
        try:
            result_form = request.form.get('result')
            play.odk = request.form.get('odk')
            play.quarter = request.form.get('quarter', type = int)
            play.yard_line = request.form.get('yard_line', type=int)
            play.down = request.form.get('down', type=int)
            play.distance = request.form.get('distance', type=int)
            play.play_type = request.form.get('play_type')
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
            play.hash = request.form.get('hash')  # New field

            # update the drive result
            drive = Drive.query.get_or_404(play.drive_id)
            drive.result = result_form if result_form else "In Progress"

            db.session.commit()
            flash('Play updated successfully!', 'success')
            return redirect(url_for('drive_detail', drive_id=play.drive_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating play: {str(e)}', 'error')

    options = {}
    for param in PLAY_PARAMETERS:
        options[param] = PlayOption.query.filter_by(parameter_name=param, enabled=True).all()

    return render_template('add_play.html',
                         play=play,
                         options=options,
                         drive_id=play.drive_id)  # Add this line


@app.route('/play/<int:play_id>/delete', methods=['POST'])
@login_required
def delete_play(play_id):
    # Author: Gaivy

    try:
        play = Play.query.get_or_404(play_id)
        drive_id = play.drive_id
        db.session.delete(play)
        db.session.commit()
        flash('Play deleted successfully', 'success')

        # update drive result
        drive = Drive.query.get_or_404(drive_id)
        new_result = Play.query.filter_by(drive_id=drive_id).order_by(Play.id).all()[-1].result
        drive.result = new_result if new_result else "In Progress"
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting play: {str(e)}', 'error')
    return redirect(url_for('drive_detail', drive_id=drive_id))


# Settings routes
@app.route('/settings')
@login_required
def settings():
    # Author: Gaivy, Rashed, Yazan

    options = {}
    for param in PLAY_PARAMETERS:
        options[param] = PlayOption.query.filter_by(parameter_name=param).all()
    return render_template('settings.html', options=options, parameters=PLAY_PARAMETERS)


@app.route('/settings/option/add/<param>', methods=['POST'])
@login_required
def add_play_option(param):
    # Author: Gaivy, Rashed, Yazan

    if param not in PLAY_PARAMETERS:
        abort(404)
    value = request.form.get('value')
    option = PlayOption(parameter_name=param, value=value)
    db.session.add(option)
    db.session.commit()
    flash(f'Added option "{value}" to {PLAY_PARAMETERS[param]}')
    return redirect(url_for('settings'))


@app.route('/settings/option/<int:option_id>/toggle', methods=['POST'])
@login_required
def toggle_play_option(option_id):
    # Author: Gaivy, Rashed, Yazan

    option = PlayOption.query.get_or_404(option_id)
    option.enabled = not option.enabled
    db.session.commit()
    return redirect(url_for('settings'))


@app.route('/settings/option/<int:option_id>/delete', methods=['POST'])
@login_required
def delete_play_option(option_id):
    # Author: Gaivy, Rashed, Yazan

    option = PlayOption.query.get_or_404(option_id)
    db.session.delete(option)
    db.session.commit()
    return redirect(url_for('settings'))


@app.route('/game/<int:game_id>/drive-chart')
@login_required
def drive_chart(game_id):
    game = Game.query.get_or_404(game_id)
    drives = Drive.query.filter_by(game_id=game_id).all()

    drives_data = []
    for drive in drives:
        plays = Play.query.filter_by(drive_id=drive.id).order_by(Play.id).all()
        numberPlays = len(plays)

        start_yard = plays[0].yard_line
        end_yard = plays[numberPlays-1].yard_line
        if start_yard < 0:
            start_yard = start_yard*(-1)
            print(start_yard)
        else:
            start_yard = start_yard+50
        if end_yard < 0:
            end_yard = end_yard*(-1)
            print(end_yard)
        if end_yard != 50 and end_yard > 0:
            end_yard = end_yard

        #if plays and plays[-1].gain_loss:
            #end_yard += plays[-1].gain_loss

        if drive.result and drive.result.lower() == 'touchdown':
            end_yard = 100

        start_yard = max(0, min(100, start_yard))
        end_yard = max(0, min(100, end_yard))

        # Detect loss for this specific drive
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
            'loss': loss_detected  # Store as a boolean, not a string
        })
    print(f"Drives Data: {drives_data}")
    return render_template('drive_chart.html', game=game, drives=drives_data, max=max)

@app.route('/drive/<int:drive_id>/export')
@login_required
def export_drive(drive_id):
    # Author: Gaivy

    drive = Drive.query.get_or_404(drive_id)
    plays = Play.query.filter_by(drive_id=drive.id).order_by(Play.id).all()

    csv_data = io.StringIO()
    writer = csv.writer(csv_data)
    writer.writerow([
        'Play #', 'ODK', 'Quarter', 'Down', 'Distance', 'Yard Line', 'Play Type', 'Result',
        'Gain/Loss', 'Personnel', 'Formation', 'Strength', 'Adjustment', 'Motion', 'Protection',
        'Play Call', 'Direction', 'Tag', 'Hash'
    ])

    for index_, play in enumerate(plays, start=1): # index shadows a variable from the outer scoper
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

@app.route('/game/<int:game_id>/export')
@login_required
def export_game(game_id):
    # Author: Gaivy, Rashed

    game = Game.query.get_or_404(game_id)
    drives = Drive.query.filter_by(game_id=game.id).order_by(Drive.id).all()

    csv_data = io.StringIO()
    writer = csv.writer(csv_data, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow([
        'Drive #', 'Play #', 'ODK', 'Quarter', 'Down', 'Distance', 'Yard Line', 'Play Type', 'Result',
        'Gain/Loss', 'Personnel', 'Formation', 'Strength', 'Adjustment', 'Motion', 'Protection',
        'Play Call', 'Direction', 'Tag', 'Hash'
    ])

    for drive_index, drive in enumerate(drives, start=1):
        plays = Play.query.filter_by(drive_id=drive.id).order_by(Play.id).all()
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

# Gaivy
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
    app.run(port=5001, host='0.0.0.0', debug=True)