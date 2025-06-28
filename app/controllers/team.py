from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.team import TeamModel
from app.models.user import UserModel

team_bp = Blueprint('team', __name__, url_prefix='/team')

@team_bp.route('/create', methods=['GET', 'POST'])
def create_team():
    base_folder = os.path.join(current_app.static_folder, "team_creation_assets", "base")
    icon_folder = os.path.join(current_app.static_folder, "team_creation_assets", "icons")
    user_created_folder = os.path.join(current_app.static_folder, "user_created_icons")
    os.makedirs(user_created_folder, exist_ok=True)

    base_files = [f for f in sorted(os.listdir(base_folder)) if f.endswith('.svg')]
    icon_filenames = [f for f in sorted(os.listdir(icon_folder)) if f.endswith(('.svg', '.png'))]

    if request.method == 'POST':
        name = request.form.get('name')
        primary_color = request.form.get('primary_color')
        secondary_color = request.form.get('secondary_color')
        icon_file = request.form.get('icon_filename')
        final_svg = request.form.get('final_svg')
        uploaded_icon = request.files.get('icon-upload')

        # Validate required fields
        if not name or not primary_color or not secondary_color or not final_svg:
            flash('All fields are required.', 'danger')
            return redirect(request.url)

        # Check if team name already exists
        if TeamModel.query.filter_by(name=name).first():
            flash(f'Team name "{name}" already exists. Please choose another.', 'danger')
            return redirect(request.url)

        safe_name = secure_filename(name)
        team_folder = os.path.join(user_created_folder, safe_name)
        os.makedirs(team_folder, exist_ok=True)

        # Save uploaded icon if provided
        if uploaded_icon and uploaded_icon.filename != '':
            uploaded_filename = secure_filename(uploaded_icon.filename)
            uploaded_path = os.path.join(team_folder, uploaded_filename)
            uploaded_icon.save(uploaded_path)
            icon_file = uploaded_filename

        # Save the final SVG output
        svg_path = os.path.join(team_folder, "team_icon.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(final_svg)

        # Optional: generate PNG preview version
        # You could add CairoSVG here if needed

        # Build URL to be saved in DB
        icon_path = url_for('static', filename=f'user_created_icons/{safe_name}/team_icon.svg')

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

    return render_template(
        'team/create_team.html',
        base_files=base_files,
        icon_filenames=icon_filenames
    )
