from flask import Flask, render_template
from flask_login import LoginManager

from app.extensions import db
from app.models.user import UserModel
from app.models.play_option import PlayOptionModel
from app.models.play_call import PlayCallModel
from app.config import ApplicationData as AD

from app.controllers.user import UserController
from app.controllers.user_management import UserManagementController
from app.controllers.game import GameController
from app.controllers.drive import DriveController
from app.controllers.play import PlayController
from app.controllers.call_sheet import CallSheetController
from app.controllers.settings import SettingsController


class PlaybookApp:
    app: Flask
    login_manager: LoginManager

    def __init__(self) -> None:
        self.app = Flask(
            __name__,
            static_folder='app/static',
            static_url_path='/static',
            template_folder='app/templates'
        )

        self.app.config.from_object('app.config.ServerConfig')

        self.login_manager = LoginManager()
        self.login_manager.login_view = 'login'

        db.init_app(self.app)
        self.login_manager.init_app(self.app)

        self._register_controllers()
        self._inject_context()
        self._register_error_handlers()

    def _register_controllers(self) -> None:
        UserController(app=self.app, login_manager=self.login_manager, teams_data=AD.TEAMS_DATA)
        UserManagementController(app=self.app)
        GameController(app=self.app)
        DriveController(app=self.app, play_parameters=AD.PLAY_PARAMETERS)
        PlayController(app=self.app, play_parameters=AD.PLAY_PARAMETERS)
        CallSheetController(app=self.app)
        SettingsController(app=self.app, play_parameters=AD.PLAY_PARAMETERS)

    def _inject_context(self) -> None:
        @self.app.context_processor
        def inject_teams() -> dict:
            return dict(teams=AD.TEAMS_DATA)

    def _register_error_handlers(self) -> None:
        @self.app.errorhandler(403)
        def forbidden(error):
            return render_template("errors/403.html"), 403

        @self.app.errorhandler(404)
        def not_found(error):
            return render_template("errors/404.html"), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return render_template("errors/500.html"), 500

    def initialize_database(self) -> None:
        with self.app.app_context():
            db.create_all()
            self._ensure_play_calls()
            self._ensure_play_options()
            self._create_test_user()
            db.session.commit()

    @staticmethod
    def _create_test_user():
        from werkzeug.security import generate_password_hash
        password = generate_password_hash('dev.null')

        existing = UserModel.query.filter_by(username='dev.null').first()
        if not existing:
            test_user = UserModel(
                username='dev.null',
                password=password,
                role='admin'
            )
            db.session.add(test_user)
            print("[+] Test user 'dev.null' created.")
        else:
            print("[=] Test user 'dev.null' already exists.")

    @staticmethod
    def _ensure_play_calls() -> None:
        for name in AD.PLAY_CALLS:
            existing = PlayCallModel.query.filter(
                db.func.lower(PlayCallModel.name) == name.lower()
            ).first()

            if not existing:
                call = PlayCallModel(name=name.upper(), status=True)
                db.session.add(call)
                print(f"[+] Play Call '{name}' added.")
            else:
                print(f"[=] Play Call '{name}' already exists.")

    @staticmethod
    def _ensure_play_options() -> None:
        # Verzeihung - wird später als sys.argv | argparse --dev-mode=True
        # Else - useless
        import random
        for name, value, *_ in AD.PLAY_OPTIONS:
            exists = PlayOptionModel.query.filter_by(parameter_name=name, value=value).first()
            if not exists:
                option = PlayOptionModel(parameter_name=name, value=value, enabled=True)

                if name == 'off_play':
                    call_ids = [c.id for c in PlayCallModel.query.all()]
                    if call_ids:
                        option.play_call_id = random.choice(call_ids)
                        print(f"[+] Play Option '{name}' -> '{value}' associated with call ID {option.play_call_id}")

                db.session.add(option)
                print(f"[+] Play Option '{name}' -> '{value}' added.")
            else:
                updated = False
                if name == 'off_play' and exists.play_call_id is None:
                    call_ids = [c.id for c in PlayCallModel.query.all()]
                    if call_ids:
                        exists.play_call_id = random.choice(call_ids)
                        updated = True
                        print(f"[~] Updated Play Option '{name}' -> '{value}' with call ID {exists.play_call_id}")

                if not updated:
                    print(f"[=] Play Option '{name}' -> '{value}' already exists.")

    def run(self) -> None:
        self.app.run(host='127.0.0.1', port=8080, debug=True)


def main():
    app_instance = PlaybookApp()
    try:
        print("Database initialization ...")
        app_instance.initialize_database()
    except Exception as err:
        print(f"Database initialization error: {str(err)}, Type: {type(err).__name__}")
    print("Starting application ...")
    app_instance.run()


if __name__ == '__main__':
    main()
