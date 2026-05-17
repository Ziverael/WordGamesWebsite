import os
from flask import Flask, render_template
from flask import Blueprint

# from .config import config


def create_app(config_name = "default"):
    """Function factory"""

    app = Flask(__name__)

    from .main import main as main_bp
    app.register_blueprint(main_bp, url_prefix = "/")

    from .math import math as math_bp
    app.register_blueprint(math_bp)

    from .spanish import spanish as spanish_bp
    app.register_blueprint(spanish_bp)

    from .english import english as english_bp
    app.register_blueprint(english_bp)

    return app
