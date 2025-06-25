import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.team import TeamModel

team_bp = Blueprint('team', __name__, url_prefix='/team')

@team_bp.route('/create', methods=['GET', 'POST'])
def create_team():
    svg_list = []
    shapes_dir = os.path.join(current_app.static_folder, "shapes")
    try:
        for filename in sorted(os.listdir(shapes_dir))[:8]:
            if filename.endswith(".svg"):
                with open(os.path.join(shapes_dir, filename), "r", encoding="utf-8") as f:
                    svg_list.append(f.read())
    except Exception as e:
        print(f"[!] Failed to load SVGs: {str(e)}")

    if request.method == 'POST':
        name = request.form.get('name')
        primary_color = request.form.get('primary_color')
        secondary_color = request.form.get('secondary_color')
        icon_file = request.files.get('icon')

        if not name or not primary_color or not secondary_color or not icon_file:
            flash('All fields are required.', 'danger')
            return redirect(request.url)

        if icon_file.filename == '' or not icon_file.filename.lower().endswith('.png'):
            flash('Only PNG files are allowed.', 'danger')
            return redirect(request.url)

        filename = secure_filename(icon_file.filename)
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        save_path = os.path.join(upload_folder, filename)
        icon_file.save(save_path)

        icon_url = url_for('static', filename=f'uploads/{filename}')

        new_team = TeamModel(
            name=name,
            icon=icon_url,
            primary_color=primary_color,
            secondary_color=secondary_color
        )

        db.session.add(new_team)
        db.session.commit()

        flash(f'Team "{name}" created successfully!', 'success')
        return redirect(url_for('team.create_team'))

    return render_template('team/create_team.html', svg_list=svg_list)
