from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import UserModel
from functools import wraps


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return func(*args, **kwargs)
    return decorated_view


class UserManagementController:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule('/users', view_func=self.user_list)
        self.app.add_url_rule('/users/add', view_func=self.add_user, methods=['GET', 'POST'])
        self.app.add_url_rule('/users/<int:user_id>/edit', view_func=self.edit_user, methods=['GET', 'POST'])
        self.app.add_url_rule('/users/<int:user_id>/delete', view_func=self.delete_user, methods=['POST'])
        self.app.add_url_rule('/users/<int:user_id>/reset-password', view_func=self.reset_password, methods=['GET', 'POST'])

    @login_required
    def user_list(self):
        users = UserModel.query.all()
        return render_template('user/user_list.html', users=users)

    @login_required
    @admin_required
    def add_user(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role', 'user')

            if UserModel.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('add_user'))

            hashed_password = generate_password_hash(password, method='scrypt')
            user = UserModel(username=username, password=hashed_password, role=role)
            db.session.add(user)
            db.session.commit()
            flash('User added successfully', 'success')
            return redirect(url_for('user_list'))

        return render_template('user/user_add.html')

    @login_required
    @admin_required
    def edit_user(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        if request.method == 'POST':
            user.username = request.form['username']
            user.role = request.form['role']
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('user_list'))

        return render_template('user/user_edit.html', user=user)

    @login_required
    @admin_required
    def delete_user(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
        return redirect(url_for('user_list'))

    @login_required
    def reset_password(self, user_id):
        if current_user.id != user_id and current_user.role != 'admin':
            abort(403)

        user = UserModel.query.get_or_404(user_id)

        if request.method == 'POST':
            new_password = request.form['new_password']
            user.password = generate_password_hash(new_password, method='scrypt')
            db.session.commit()
            flash('Password reset successfully', 'success')
            return redirect(url_for('game_options'))

        return render_template('user/user_reset_password.html', user=user)
