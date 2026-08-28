from word_games.config.app import APP_SETTINGS
from word_games.config.smtp import SMTP_SETTINGS


def test_app_exists(app, db_session):
    # when
    from flask import current_app  # noqa: PLC0415

    # then
    assert current_app is not None


def test_app_config_mapping(app, db_session):
    # when
    from flask import current_app  # noqa: PLC0415

    # then
    assert (
        current_app.config["SQLALCHEMY_DATABASE_URI"]
        == APP_SETTINGS.database_connection_string
    )
    assert current_app.config["SECRET_KEY"] == APP_SETTINGS.secret_key
    assert current_app.config["DEBUG"] == APP_SETTINGS.debug
    assert "env" not in current_app.config


def test_app_config_mapping_smtp(app, db_session):
    # when
    from flask import current_app  # noqa: PLC0415

    # then
    assert current_app.config["MAIL_SERVER"] == SMTP_SETTINGS.server
    assert current_app.config["MAIL_PORT"] == SMTP_SETTINGS.port
    assert current_app.config["MAIL_USE_TLS"] == SMTP_SETTINGS.use_tls
    assert current_app.config["MAIL_USE_SSL"] == SMTP_SETTINGS.use_ssl
    assert current_app.config["MAIL_USERNAME"] == SMTP_SETTINGS.username
    assert current_app.config["MAIL_PASSWORD"] == SMTP_SETTINGS.password
    assert (
        current_app.config["MAIL_DEFAULT_SENDER"]
        == SMTP_SETTINGS.default_sender
    )


def test_app_blueprints(app, db_session):
    # given
    # ruff: disable[PLC0415]
    from word_games.view.auth import auth as auth_bp
    from word_games.view.game import game as game_bp
    from word_games.view.game_editor import game_editor as game_editor_bp
    from word_games.view.main import main as main_bp
    from word_games.view.profile import profile as profile_bp

    # ruff: enable[PLC0415]
    bps = [main_bp, auth_bp, game_editor_bp, profile_bp, game_bp]

    # when
    from flask import current_app  # noqa: PLC0415

    registered_bps = current_app.blueprints.values()

    # then
    assert all(bp in registered_bps for bp in bps)
    assert len(registered_bps) == len(bps)
