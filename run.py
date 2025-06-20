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
            self._ensure_play_options()
            db.session.commit()

    @staticmethod
    def _ensure_play_options() -> None:
        for name, value in AD.PLAY_OPTIONS:
            exists = PlayOptionModel.query.filter_by(parameter_name=name, value=value).first()
            if not exists:
                option = PlayOptionModel(parameter_name=name, value=value, enabled=True)
                db.session.add(option)

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
