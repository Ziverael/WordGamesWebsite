from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from word_games.database import BaseTable


def page_not_found(_error):
    return render_template("error.html"), 404


csrf = CSRFProtect()
db = SQLAlchemy(model_class=BaseTable)


def create_app():
    """Function factory"""
    from word_games.config.app import APP_SETTINGS

    app = Flask(__name__)
    app.config.from_object(APP_SETTINGS)
    app.register_error_handler(404, page_not_found)

    db.init_app(app)
    csrf.init_app(app)

    from word_games.view.main import main as main_bp

    app.register_blueprint(main_bp, url_prefix="/")

    from word_games.view.auth import auth as auth_bp

    app.register_blueprint(auth_bp)

    from word_games.view.creator import creator as creator_bp

    app.register_blueprint(creator_bp)

    return app
