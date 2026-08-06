from typing import TYPE_CHECKING, Any, cast
from unittest.mock import Mock

import pytest

from word_games.view.auth import forms


if TYPE_CHECKING:
    from flask_wtf import FlaskForm


@pytest.mark.parametrize(
    ("password", "msg"),
    [
        ("", r"Password must be at least 12 characters long."),
        ("a", r"Password must be at least 12 characters long."),
        ("blackjacked", r"Password must be at least 12 characters long."),
        ("1234567890!@", r"Password must contain an uppercase letter."),
        ("1234567890ab", r"Password must contain an uppercase letter."),
        ("1234567890A@", r"Password must contain a lowercase letter."),
        ("Clickjacking", r"Password must contain a number."),
        ("Clickjacking2", r"Password must contain a special character."),
        ("Clickj@cking 2", r"Password cannot contain spaces."),
    ],
)
def test_check_password_complexity__invalid(password: str, msg: str):
    # given
    form = cast("FlaskForm", "dummy_form")
    field = Mock()
    field.data = password

    # when / then
    with pytest.raises(forms.ValidationError, match=msg):
        forms.check_password_complexity(form, field)


@pytest.mark.parametrize(
    "password",
    [
        r"Clickj@cking2",
        r"Km35yVEzKE%T`PwyvJr@49W~`NFPwb`ZicV9xtyKUyJtmgupaeFes@kJx5mJFdWN",
        r"}`s=oLZ[~7!A-=mcL;DW}w;RLRsWerMZ-g5&\q%$<[kVVZQ.aQE~x`4F=Qj+cM_>",
        r"þdÿïÊCKÞ/Wûøj`¢L3ÄòëÂÙtç¢Ë9ÂÆçÇÅLh#*¥]F4¹>$HDp<T=%Ò'.:µÖc>X!~Ãp9",
        r"猫🐱Ú¬à-P<K_ÚE¸w¾:]æ½m[#)?³eº¶ºk4¹Îãë+'ÍPh«î©ËUî)cZ(TT½xaí_/ÖSuNæÛ",  # noqa: RUF001
    ],
)
def test_check_password_complexity__valid(password: str):
    # given
    form = cast("FlaskForm", "dummy_form")
    field = Mock()
    field.data = password

    # when
    forms.check_password_complexity(form, field)

    # then
    assert True


class TestLoginForm:
    @pytest.mark.parametrize("remember_me", [True, False, "false", ""])
    def test_valid(self, app_for_forms, remember_me: bool):
        # when
        with app_for_forms.test_request_context():
            form = forms.LoginForm(
                data={
                    "email": "dummy@somewhere.com",
                    "password": r"Clickj@cking2",
                    "remember_me": remember_me,
                }
            )
            # then
            assert form.validate()
            assert form.errors == {}

    @pytest.mark.parametrize(
        ("data", "errors"),
        [
            (
                {
                    "email": "",
                    "password": r"Clickj@cking2",
                    "remember_me": True,
                },
                {"email": ["This field is required."]},
            ),
            (
                {
                    "email": "i" * 128 + "@dummy.com",
                    "password": r"Clickj@cking2",
                    "remember_me": True,
                },
                {"email": ["Field must be between 1 and 128 characters long."]},
            ),
            (
                {
                    "email": "not.an.email",
                    "password": r"Clickj@cking2",
                    "remember_me": True,
                },
                {"email": ["Invalid email address."]},
            ),
            (
                {
                    "email": "dummy@somewhere.com",
                    "password": r"",
                    "remember_me": True,
                },
                {"password": ["This field is required."]},
            ),
        ],
    )
    def test_invalid(
        self, app_for_forms, data: dict[str, Any], errors: list[str]
    ):
        # when
        with app_for_forms.test_request_context():
            form = forms.LoginForm(data=data)
            # then
            assert not form.validate()
            assert form.errors == errors
