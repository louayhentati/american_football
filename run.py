from flask import Flask
from flask_login import LoginManager

from app.extensions import db
from app.models.user import UserModel
from app.models.play_option import PlayOptionModel
from app.models.play_call import PlayCallModel
from app.models.team import TeamModel
from app.config import ApplicationData as AD

from app.controllers.user import UserController
from app.controllers.user_management import UserManagementController
from app.controllers.game import GameController
from app.controllers.drive import DriveController
from app.controllers.play import PlayController
from app.controllers.call_sheet import CallSheetController
from app.controllers.settings import SettingsController
from app.controllers.error import ErrorController
from app.controllers.team import team_bp

class PlaybookApp:
    app: Flask
    login_manager: LoginManager

    def __init__(self) -> None:
        print("Initializing Application...")
        try:
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

            print("Application initialized successfully")
        except Exception as e:
            print(f"[!] Initialization error: {str(e)} ({type(e).__name__})")

    def _register_controllers(self) -> None:
        try:
            print("Registering controllers...")
            UserController(app=self.app, login_manager=self.login_manager)
            UserManagementController(app=self.app)
            GameController(app=self.app)
            DriveController(app=self.app, play_parameters=AD.PLAY_PARAMETERS)
            PlayController(app=self.app, play_parameters=AD.PLAY_PARAMETERS)
            CallSheetController(app=self.app)
            SettingsController(app=self.app, play_parameters=AD.PLAY_PARAMETERS)
            ErrorController(app=self.app)
            self.app.register_blueprint(team_bp)
            print("Controllers registered successfully")
        except Exception as e:
            print(f"[!] Controller registration error: {str(e)} ({type(e).__name__})")

    def _inject_context(self) -> None:
        @self.app.context_processor
        def inject_teams() -> dict:
            try:
                teams = TeamModel.query.all()
                return dict(teams=teams)
            except Exception as e:
                print(f"[!] Error injecting teams: {str(e)} ({type(e).__name__})")
                return dict(teams=[])

    @staticmethod
    def _ensure_play_calls() -> None:
        for name in AD.PLAY_CALLS:
            try:
                existing = PlayCallModel.query.filter(
                    db.func.lower(PlayCallModel.name) == name.lower()
                ).first()
                if not existing:
                    call = PlayCallModel(name=name.upper(), status=True)
                    db.session.add(call)
                    print(f"[+] Play Call '{name}' added")
                else:
                    print(f"[=] Play Call '{name}' already exists")
            except Exception as e:
                print(f"[!] Error processing Play Call '{name}': {str(e)} ({type(e).__name__})")

    @staticmethod
    def _ensure_play_options() -> None:
        import random
        for name, value, *_ in AD.PLAY_OPTIONS:
            try:
                exists = PlayOptionModel.query.filter_by(parameter_name=name, value=value).first()
                if not exists:
                    option = PlayOptionModel(parameter_name=name, value=value, enabled=True)
                    if name == 'off_play':
                        call_ids = [c.id for c in PlayCallModel.query.all()]
                        if call_ids:
                            option.play_call_id = random.choice(call_ids)
                    db.session.add(option)
                    print(f"[+] Play Option '{name}' -> '{value}' added")
                else:
                    if name == 'off_play' and exists.play_call_id is None:
                        call_ids = [c.id for c in PlayCallModel.query.all()]
                        if call_ids:
                            exists.play_call_id = random.choice(call_ids)
                            print(f"[~] Updated Play Option '{name}' -> '{value}' with call ID {exists.play_call_id}")
                    else:
                        print(f"[=] Play Option '{name}' -> '{value}' already exists")
            except Exception as e:
                print(f"[!] Error processing Play Option '{name}' -> '{value}': {str(e)} ({type(e).__name__})")

    def run(self) -> None:
        try:
            self.app.run(host='127.0.0.1', port=8080, debug=True)
        except Exception as e:
            print(f"[!] Application failed to start: {str(e)} ({type(e).__name__})")


def main():
    app_instance = PlaybookApp()
    app_instance.run()


if __name__ == '__main__':
    main()
