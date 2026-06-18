from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from word_games.db import get_session, register_db_cleanup


def page_not_found(_error):
    return render_template("error.html"), 404


csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.login_view = "word_games.view.auth.login"


from word_games.db_table import User


@login_manager.user_loader
def load_user(user_id):
    session = get_session()
    return session.get(User, int(user_id))


def create_app():
    """Function factory"""
    from word_games.config.app import APP_SETTINGS

    app = Flask(__name__)
    app.config.from_object(APP_SETTINGS)
    app.register_error_handler(404, page_not_found)

    csrf.init_app(app)
    login_manager.init_app(app)

    register_db_cleanup(app)

    from word_games.view.main import main as main_bp

    app.register_blueprint(main_bp, url_prefix="/")

    from word_games.view.auth import auth as auth_bp

    app.register_blueprint(auth_bp)

    from word_games.view.creator import creator as creator_bp

    app.register_blueprint(creator_bp)

    return app
