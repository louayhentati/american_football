from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import UserModel
from app.models.team import TeamModel
from functools import wraps

assign_bp = Blueprint('assign_team', __name__, url_prefix='/assign')


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return func(*args, **kwargs)

    return decorated_view


@assign_bp.route('/team', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_team():
    users = UserModel.query.all()
    teams = TeamModel.query.all()

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        team_id = request.form.get('team_id')

        user = UserModel.query.get(user_id)
        if user:
            user.team_id = team_id
            db.session.commit()

            # If current user is the one updated, update session too
            if current_user.id == user.id:
                assigned_team = TeamModel.query.get(team_id)
                session['team_color'] = assigned_team.primary_color if assigned_team else None
                session['team_id'] = int(team_id) if assigned_team else None

            flash('Team assigned successfully!', 'success')
        else:
            flash('User not found.', 'danger')

        return redirect(url_for('assign_team.assign_team'))

    return render_template('user/user_assign_team.html', users=users, teams=teams)
