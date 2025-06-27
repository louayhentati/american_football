from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.team import TeamModel
from app.models.user import UserModel

team_bp = Blueprint('team', __name__, url_prefix='/team')  # <-- define first!

@team_bp.route('/create', methods=['GET', 'POST'])
def create_team():
    base_folder = os.path.join(current_app.static_folder, "team_creation_assets", "base")
    icon_folder = os.path.join(current_app.static_folder, "team_creation_assets", "icons")
    user_created_folder = os.path.join(current_app.static_folder, "user_created_icons")
    os.makedirs(user_created_folder, exist_ok=True)  # Ensure the folder exists

    base_files = [f for f in sorted(os.listdir(base_folder)) if f.endswith('.svg')]
    icon_filenames = [f for f in sorted(os.listdir(icon_folder)) if f.endswith(('.svg', '.png'))]

    if request.method == 'POST':
        name = request.form.get('name')
        primary_color = request.form.get('primary_color')
        secondary_color = request.form.get('secondary_color')
        icon_file = request.form.get('icon_filename')
        final_svg = request.form.get('final_svg')  # Get the serialized SVG string

        uploaded_icon = request.files.get('icon-upload')
        if uploaded_icon and uploaded_icon.filename != '':
            filename = secure_filename(uploaded_icon.filename)
            save_path = os.path.join(icon_folder, filename)
            uploaded_icon.save(save_path)
            icon_file = filename  # override with uploaded file

        if not name or not primary_color or not secondary_color or not icon_file or not final_svg:
            flash('All fields are required.', 'danger')
            return redirect(request.url)

        
        team_folder = os.path.join(user_created_folder, secure_filename(name))
        os.makedirs(team_folder, exist_ok=True)

        svg_path = os.path.join(team_folder, "team_icon.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(final_svg)

        icon_path = url_for('static', filename=f'user_created_icons/{secure_filename(name)}/team_icon.svg')

        new_team = TeamModel(
            name=name,
            icon=icon_path,
            primary_color=primary_color,
            secondary_color=secondary_color
        )

        db.session.add(new_team)
        db.session.commit()

        flash(f'Team "{name}" created successfully!', 'success')
        return redirect(url_for('team.create_team'))

    return render_template('team/create_team.html', base_files=base_files, icon_filenames=icon_filenames)




@team_bp.route('/list')
def list_all_teams():
    teams = TeamModel.query.all()

    # Query all users with team_id in the teams list
    team_ids = [team.id for team in teams]
    if not team_ids:
        return render_template(
            'team/show_teams.html',
            teams=[],
            team_members={}
        )

    users = UserModel.query.filter(UserModel.team_id.in_(team_ids)).all()
    team_members = {}
    for user in users:
        team_members.setdefault(user.team_id, []).append(user)

    return render_template(
        'team/show_teams.html',
        teams=teams,
        team_members=team_members
    )

