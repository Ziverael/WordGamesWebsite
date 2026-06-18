def test_app_exists(app, db_session):
    # when
    from flask import current_app  # noqa: PLC0415

    # then
    assert current_app is not None
