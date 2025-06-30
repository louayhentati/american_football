from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

from app.models.user import UserModel


class UserController:
    def __init__(self, app: Flask, login_manager: LoginManager) -> None:
        self.app = app
        self.login_manager = login_manager
        self.register_routes()

    def register_routes(self) -> None:
        self.login_manager.user_loader(self.load_user)
        self.app.add_url_rule(rule='/', view_func=self.index)
        self.app.add_url_rule(rule='/login', view_func=self.login, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/logout', view_func=self.logout)

    @staticmethod
    def load_user(user_id):
        return UserModel.query.get(int(user_id))

    @staticmethod
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('game_options'))
        return render_template('auth/login.html')

    @staticmethod
    def login():
        session.clear()
        if current_user.is_authenticated:
            return redirect(url_for('game_options'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = UserModel.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                login_user(user)

                if user.team_id:
                    session['team_id'] = user.team_id
                    session['team_name'] = user.team.name
                    session['team_color'] = user.team.primary_color
                    session['team_icon'] = user.team.icon
                flash('Login successful!', 'success')
                return redirect(url_for('game_options'))

            flash('Invalid username or password', 'danger')

        return render_template('auth/login.html')

    @login_required
    def logout(self):
        logout_user()
        flash('who are you ?', 'success')
        session.clear()
        return redirect(url_for('login'))
