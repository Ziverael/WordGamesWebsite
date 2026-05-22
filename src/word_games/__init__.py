from flask import Flask, render_template


def page_not_found(_error):
    return render_template("error.html"), 404


def create_app(_config_name: str = "default"):
    """Function factory"""

    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)

    from word_games.view.main import main as main_bp

    app.register_blueprint(main_bp, url_prefix="/")

    from word_games.view.auth import auth as auth_bp

    app.register_blueprint(auth_bp)

    from word_games.view.creator import creator as creator_bp

    app.register_blueprint(creator_bp)

    return app
