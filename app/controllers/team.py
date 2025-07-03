from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.team import TeamModel
from app.models.user import UserModel
from PIL import Image
from collections import Counter

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

        if not name or not primary_color or not secondary_color or not final_svg:
            flash('All fields are required.', 'danger')
            return redirect(request.url)

        if TeamModel.query.filter_by(name=name).first():
            flash(f'Team name "{name}" already exists. Please choose another.', 'danger')
            return redirect(request.url)

        safe_name = secure_filename(name)
        team_folder = os.path.join(user_created_folder, safe_name)
        os.makedirs(team_folder, exist_ok=True)

        if uploaded_icon and uploaded_icon.filename != '':
            uploaded_filename = secure_filename(uploaded_icon.filename)
            uploaded_path = os.path.join(team_folder, uploaded_filename)
            uploaded_icon.save(uploaded_path)
            icon_file = uploaded_filename

        svg_path = os.path.join(team_folder, "team_icon.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(final_svg)

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


@team_bp.route('/list')
def list_all_teams():
    teams = TeamModel.query.all()
    team_ids = [team.id for team in teams]

    if not team_ids:
        return render_template('team/show_teams.html', teams=[], team_members={})

    users = UserModel.query.filter(UserModel.team_id.in_(team_ids)).all()
    team_members = {}
    for user in users:
        team_members.setdefault(user.team_id, []).append(user)

    return render_template(
        'team/show_teams.html',
        teams=teams,
        team_members=team_members
    )


@team_bp.route('/delete/<int:team_id>', methods=['POST'])
def delete_team(team_id):
    team = TeamModel.query.get_or_404(team_id)

    users_assigned = UserModel.query.filter_by(team_id=team_id).all()
    if users_assigned:
        flash('Cannot delete team while users are assigned to it.', 'danger')
        return redirect(url_for('team.list_all_teams'))

    from shutil import rmtree

    safe_name = team.name.replace(" ", "_")
    team_folder_path = os.path.join(current_app.static_folder, 'user_created_icons', safe_name)

    if os.path.exists(team_folder_path):
        try:
            rmtree(team_folder_path)
        except Exception as e:
            flash(f"Error deleting team files: {str(e)}", 'danger')
            return redirect(url_for('team.list_all_teams'))

    db.session.delete(team)
    db.session.commit()

    flash(f"Team '{team.name}' has been deleted successfully.", 'success')
    return redirect(url_for('team.list_all_teams'))


@team_bp.route('/choice')
def choose_creation_method():
    return render_template('team/user_choice.html')


def extract_dominant_colors(file_storage):
    try:
        img = Image.open(file_storage.stream).convert("RGBA")
        img = img.resize((64, 64))
        pixels = [pixel for pixel in img.getdata() if pixel[3] > 0]
        rgb_pixels = [(r, g, b) for r, g, b, _ in pixels]

        most_common = Counter(rgb_pixels).most_common(2)
        hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in [c[0] for c in most_common]]

        if len(hex_colors) == 1:
            hex_colors.append("#ffffff")
        elif len(hex_colors) == 0:
            hex_colors = ["#000000", "#ffffff"]

        return hex_colors[0], hex_colors[1]
    except Exception as e:
        print("Color extraction failed:", e)
        return "#000000", "#ffffff"


@team_bp.route('/upload_icon', methods=['GET', 'POST'])
def upload_team_icon_page():
    user_created_folder = os.path.join(current_app.static_folder, "user_created_icons")
    os.makedirs(user_created_folder, exist_ok=True)

    if request.method == 'POST':
        name = request.form.get('name')
        final_svg = request.form.get('final_svg')
        uploaded_icon = request.files.get('icon')

        if not name or not uploaded_icon or not final_svg:
            flash('All fields are required.', 'danger')
            return redirect(request.url)

        if TeamModel.query.filter_by(name=name).first():
            flash(f'Team name "{name}" already exists.', 'danger')
            return redirect(request.url)

        safe_name = secure_filename(name)
        team_folder = os.path.join(user_created_folder, safe_name)
        os.makedirs(team_folder, exist_ok=True)

        uploaded_filename = secure_filename(uploaded_icon.filename)
        uploaded_path = os.path.join(team_folder, uploaded_filename)
        uploaded_icon.stream.seek(0)
        uploaded_icon.save(uploaded_path)

        uploaded_icon.stream.seek(0)
        primary_color, secondary_color = extract_dominant_colors(uploaded_icon)

        svg_path = os.path.join(team_folder, "team_icon.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(final_svg)

        icon_path = url_for('static', filename=f'user_created_icons/{safe_name}/team_icon.svg')

        new_team = TeamModel(
            name=name,
            icon=icon_path,
            primary_color=primary_color,
            secondary_color=secondary_color
        )

        db.session.add(new_team)
        db.session.commit()

        flash(f'Team "{name}" uploaded and saved successfully!', 'success')
        return redirect(url_for('team.list_all_teams'))

    return render_template('team/upload_team_icon.html')
