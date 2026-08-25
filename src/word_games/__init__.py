from flask import Flask, render_template

from word_games.db import get_session, register_db_cleanup
from word_games.email.app_init import get_email_service
from word_games.extensions import extensions_manager
from word_games.user.db import User


@extensions_manager.login_manager.user_loader
def load_user(user_id):
    with get_session() as session:
        return session.get(User, int(user_id))


def page_not_found(_error):
    return render_template("error.html"), 404


extensions_manager.login_manager.login_view = "auth.login"


def create_app():
    """Function factory"""
    from word_games.config.app import APP_SETTINGS
    from word_games.config.smtp import SMTP_SETTINGS

    app = Flask(__name__)
    app.config.from_mapping(APP_SETTINGS.model_dump(by_alias=True))
    app.config.update(**SMTP_SETTINGS.model_dump(by_alias=True))
    app.register_error_handler(404, page_not_found)

    extensions_manager.csrf.init_app(app)
    extensions_manager.login_manager.init_app(app)
    app.extensions["email_service"] = get_email_service(app)

    register_db_cleanup(app)

    from word_games.view.main import main as main_bp

    app.register_blueprint(main_bp, url_prefix="/")

    from word_games.view.auth import auth as auth_bp

    app.register_blueprint(auth_bp)

    from word_games.view.game_editor import game_editor as game_editor_bp

    app.register_blueprint(game_editor_bp)

    from word_games.view.profile import profile as profile_bp

    app.register_blueprint(profile_bp)
    return app
