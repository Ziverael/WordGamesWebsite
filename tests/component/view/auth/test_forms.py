from typing import Any

import pytest
from pytest_mock import MockFixture

from word_games.view.auth import forms


class TestRegistrationForm:
    def test_is_password_complexity_check_add_to_validators(
        self, app_for_forms
    ):
        # when
        with app_for_forms.test_request_context():
            form = forms.RegistrationForm()
            # then
            assert forms.check_password_complexity in form.password.validators

    @pytest.mark.parametrize(
        "data",
        [
            {
                "email": "dummy@test.com",
                "username": "DummyUser",
                "role": "teacher",
                "password": "Clickj@cking2",
                "password_check": "Clickj@cking2",
            }
        ],
    )
    def test_valid(self, app_for_forms, db_session, data: dict[str, Any]):  # noqa: ARG002
        # when
        with app_for_forms.test_request_context():
            form = forms.RegistrationForm(data=data)
            # then
            assert form.errors == {}
            assert form.validate()

    def test_missing_required_invalid(self, app_for_forms):
        # when
        with app_for_forms.test_request_context():
            form = forms.RegistrationForm(
                data={
                    "email": "",
                    "username": "",
                    "role": "teacher",
                    "password": "",
                    "password_check": "",
                }
            )
            # then
            assert not form.validate()
            assert form.errors == {
                "email": ["This field is required."],
                "username": ["This field is required."],
                "password": ["This field is required."],
                "password_check": ["This field is required."],
            }

    @pytest.mark.parametrize(
        ("email", "errors"),
        [
            ("", ["This field is required."]),
            (
                "a" * 129,
                [
                    "Field must be between 1 and 128 characters long.",
                    "Invalid email address.",
                ],
            ),
            ("katzenjammer", ["Invalid email address."]),
            ("dupa@gmail.com", None),
            ("dupa.gmail.com", ["Invalid email address."]),
        ],
    )
    def test_email(self, app_for_forms, email: str, errors: list[str]):
        # when
        with app_for_forms.test_request_context():
            form = forms.RegistrationForm(
                data={
                    "email": email,
                    "username": "exampleuser",
                    "role": "teacher",
                    "password": "Clickj@cking2",
                    "password_check": "Clickj@cking2",
                }
            )

            # then
            is_valid = errors is None
            assert is_valid == form.validate()
            expected_errors = {} if errors is None else {"email": errors}
            assert form.errors == expected_errors

    @pytest.mark.parametrize("email", ["test@example.com", "TesT@exAmple.cOm"])
    def test_email_already_registered(
        self,
        app_for_forms,
        db_session,
        user_factory,
        mocker: MockFixture,
        email: str,
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)
        user = user_factory.build(email="test@example.com")
        db_session.add(user)
        db_session.commit()

        with app_for_forms.test_request_context():
            # when
            form = forms.RegistrationForm(
                data={
                    "email": email,
                    "username": "exampleuser",
                    "role": "teacher",
                    "password": "Clickj@cking2",
                    "password_check": "Clickj@cking2",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {"email": ["Email already registered."]}

    @pytest.mark.parametrize(
        ("username", "errors"),
        [
            ("", ["This field is required."]),
            ("a" * 33, ["Field must be between 4 and 32 characters long."]),
            ("app", ["Field must be between 4 and 32 characters long."]),
            ("duty", None),
            ("Noob", None),
            ("N0ob", None),
            ("N0.o_b1", None),
            (
                "1Noob",
                [
                    "Usernames must have only letters, numbers, dots or underscores"
                ],
            ),
            (
                " Noob",
                [
                    "Usernames must have only letters, numbers, dots or underscores"
                ],
            ),
            (
                "Noob ",
                [
                    "Usernames must have only letters, numbers, dots or underscores"
                ],
            ),
            (
                "Noo@v",
                [
                    "Usernames must have only letters, numbers, dots or underscores"
                ],
            ),
            (
                "Niła",
                [
                    "Usernames must have only letters, numbers, dots or underscores"
                ],
            ),
        ],
    )
    def test_username(self, app_for_forms, username: str, errors: list[str]):
        # when
        with app_for_forms.test_request_context():
            form = forms.RegistrationForm(
                data={
                    "email": "dummy@test.com",
                    "username": username,
                    "role": "teacher",
                    "password": "Clickj@cking2",
                    "password_check": "Clickj@cking2",
                }
            )

            # then
            is_valid = errors is None
            assert is_valid == form.validate()
            expected_errors = {} if errors is None else {"username": errors}
            assert form.errors == expected_errors

    def test_username_already_registered(
        self, app_for_forms, db_session, user_factory, mocker: MockFixture
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)
        user = user_factory.build(username="User1")
        db_session.add(user)
        db_session.commit()

        with app_for_forms.test_request_context():
            # when
            form = forms.RegistrationForm(
                data={
                    "email": "dummy@test.com",
                    "username": "User1",
                    "role": "teacher",
                    "password": "Clickj@cking2",
                    "password_check": "Clickj@cking2",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {"username": ["Username already in use."]}

    def test_username_already_registered_but_other_case(
        self, app_for_forms, db_session, user_factory, mocker: MockFixture
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)
        user = user_factory.build(username="user1")
        db_session.add(user)
        db_session.commit()

        with app_for_forms.test_request_context():
            # when
            form = forms.RegistrationForm(
                data={
                    "email": "dummy@test.com",
                    "username": "User1",
                    "role": "teacher",
                    "password": "Clickj@cking2",
                    "password_check": "Clickj@cking2",
                }
            )

            # then
            assert form.validate()
            assert form.errors == {}

    @pytest.mark.parametrize(
        ("role", "errors"),
        [
            ("teacher", None),
            ("student", None),
            ("invalid", ["Not a valid choice."]),
            ("", ["Not a valid choice."]),
        ],
    )
    def test_role(self, app_for_forms, role: str, errors: list[str]):
        # when
        with app_for_forms.test_request_context():
            form = forms.RegistrationForm(
                data={
                    "email": "dummy@test.com",
                    "username": "dummy",
                    "role": role,
                    "password": "Clickj@cking2",
                    "password_check": "Clickj@cking2",
                }
            )

            # then
            is_valid = errors is None
            assert is_valid == form.validate()
            expected_errors = {} if errors is None else {"role": errors}
            assert form.errors == expected_errors

    def test_password_match(self, app_for_forms):
        # given
        dummy_password = "Dear:Pass111-<3"  # noqa: S105

        # when
        with app_for_forms.test_request_context():
            form = forms.RegistrationForm(
                data={
                    "email": "dummy@test.com",
                    "username": "dummy",
                    "role": "teacher",
                    "password": dummy_password,
                    "password_check": dummy_password,
                }
            )

            # then
            assert form.validate()
            assert form.errors == {}

    def test_password_not_match(self, app_for_forms):
        # given
        dummy_password = "Dear:Pass111-<3"  # noqa: S105

        # when
        with app_for_forms.test_request_context():
            form = forms.RegistrationForm(
                data={
                    "email": "dummy@test.com",
                    "username": "dummy",
                    "role": "teacher",
                    "password": dummy_password,
                    "password_check": dummy_password + "_invalid",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {"password": ["Passwords must match."]}


class TestChangePasswordForm:
    @pytest.fixture
    def registered_user(self, user_factory, db_session):
        user = user_factory.build(
            id=1,
            password_hash="scrypt:32768:8:1$l3UpauchGmJNbv5n$326f646ee593e4336259abcc1bf68d8082c688d16a7baff4dcfd62a0205260fba59489f9f583b804f2839081e110bf00dbe109f452f3846e947d059a74577f3c",  # noqa: S106
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_check_password_complexity(self, app_for_forms):
        # when
        with app_for_forms.test_request_context():
            form = forms.ChangePasswordForm(
                data={
                    "old_password": "Clickj@cking1",
                    "password": "Clickj@cking3",
                    "password_new": "Clickj@cking3",
                }
            )

            # then
            assert forms.check_password_complexity in form.password.validators

    def test_old_password_match(
        self, mocker: MockFixture, db_session, registered_user, app_for_forms
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)

        # when
        with app_for_forms.test_client(user=registered_user) as client:
            client.get("/")
            form = forms.ChangePasswordForm(
                data={
                    "old_password": "Clickj@cking1",
                    "password": "Clickj@cking3",
                    "password_new": "Clickj@cking3",
                }
            )

            # then
            assert form.validate()
            assert form.errors == {}

    def test_old_password_not_match(
        self,
        mocker: MockFixture,
        app_for_forms,
        db_session,
        registered_user,
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)

        # when
        with app_for_forms.test_client(user=registered_user) as client:
            client.get("/")
            form = forms.ChangePasswordForm(
                data={
                    "old_password": "Clickj@cking2",
                    "password": "Clickj@cking3",
                    "password_new": "Clickj@cking3",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {
                "old_password": ["Old password do not match."]
            }

    def test_new_password_is_old_pasword(
        self,
        mocker: MockFixture,
        app_for_forms,
        db_session,
        registered_user,
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)

        # when
        with app_for_forms.test_client(user=registered_user) as client:
            client.get("/")
            form = forms.ChangePasswordForm(
                data={
                    "old_password": "Clickj@cking1",
                    "password": "Clickj@cking1",
                    "password_new": "Clickj@cking1",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {
                "password_new": [
                    "New password must be different from old password."
                ]
            }

    def test_missing_fields(
        self,
        mocker: MockFixture,
        app_for_forms,
        db_session,
        registered_user,
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)

        # when
        with app_for_forms.test_client(user=registered_user) as client:
            client.get("/")
            form = forms.ChangePasswordForm(
                data={
                    "old_password": "",
                    "password": "",
                    "password_new": "",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {
                "old_password": ["This field is required."],
                "password": ["This field is required."],
                "password_new": ["This field is required."],
            }

    def test_password_and_new_password_differ(
        self,
        mocker: MockFixture,
        app_for_forms,
        db_session,
        registered_user,
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)

        # when
        with app_for_forms.test_client(user=registered_user) as client:
            client.get("/")
            form = forms.ChangePasswordForm(
                data={
                    "old_password": "Clickj@cking1",
                    "password": "Clickj@cking2",
                    "password_new": "Clickj@cking3",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {
                "password": ["Passwords must match."],
            }


class TestPasswordResetRequestForm:
    @pytest.mark.parametrize(
        ("email", "errors"),
        [
            ("", ["This field is required."]),
            (
                "a" * 129,
                [
                    "Field must be between 1 and 128 characters long.",
                    "Invalid email address.",
                ],
            ),
            ("katzenjammer", ["Invalid email address."]),
            ("dupa@gmail.com", None),
            ("dupa.gmail.com", ["Invalid email address."]),
        ],
    )
    def test_email(self, app_for_forms, email: str, errors: list[str]):
        # when
        with app_for_forms.test_request_context():
            form = forms.PasswordResetRequestForm(
                data={
                    "email": email,
                }
            )

            # then
            is_valid = errors is None
            assert is_valid == form.validate()
            expected_errors = {} if errors is None else {"email": errors}
            assert form.errors == expected_errors


class TestPasswordResetForm:
    def test_is_password_complexity_check_add_to_validators(
        self, app_for_forms
    ):
        # when
        with app_for_forms.test_request_context():
            form = forms.PasswordResetForm()
            # then
            assert forms.check_password_complexity in form.password.validators

    def test_password_not_match(self, app_for_forms):
        # given
        dummy_password = "Dear:Pass111-<3"  # noqa: S105

        # when
        with app_for_forms.test_request_context():
            form = forms.PasswordResetForm(
                data={
                    "password": dummy_password,
                    "password_new": dummy_password + "_invalid",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {"password": ["Passwords must match."]}

    def test_password_match(self, app_for_forms):
        # given
        dummy_password = "Dear:Pass111-<3"  # noqa: S105

        # when
        with app_for_forms.test_request_context():
            form = forms.PasswordResetForm(
                data={
                    "password": dummy_password,
                    "password_new": dummy_password,
                }
            )

            # then
            assert form.validate()
            assert form.errors == {}

    def test_missing_values(self, app_for_forms):
        # when
        with app_for_forms.test_request_context():
            form = forms.PasswordResetForm(
                data={
                    "password": "",
                    "password_new": "",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {
                "password": ["This field is required."],
                "password_new": ["This field is required."],
            }


class TestChangeEmailForm:
    @pytest.fixture
    def registered_user(self, user_factory, db_session):
        user = user_factory.build(
            id=1,
            email="dummy@example.com",
            password_hash="scrypt:32768:8:1$l3UpauchGmJNbv5n$326f646ee593e4336259abcc1bf68d8082c688d16a7baff4dcfd62a0205260fba59489f9f583b804f2839081e110bf00dbe109f452f3846e947d059a74577f3c",  # noqa: S106
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_password_not_match(
        self,
        mocker: MockFixture,
        app_for_forms,
        db_session,
        registered_user,
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)

        # when
        with app_for_forms.test_client(user=registered_user) as client:
            client.get("/")
            form = forms.ChangeEmailForm(
                data={
                    "password": "Clickj@cking2",
                    "email": "dummy2@example.com",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {"password": ["Password is invalid."]}

    def test_missing_password(
        self,
        mocker: MockFixture,
        app_for_forms,
        db_session,
        registered_user,
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)

        # when
        with app_for_forms.test_client(user=registered_user) as client:
            client.get("/")
            form = forms.ChangeEmailForm(
                data={
                    "password": "",
                    "email": "dummy2@example.com",
                }
            )

            # then
            assert not form.validate()
            assert form.errors == {"password": ["This field is required."]}

    @pytest.mark.parametrize(
        ("email", "errors"),
        [
            ("", ["This field is required."]),
            (
                "dummy@example.com",
                ["New email should not be the current email."],
            ),
            ("dummy.example.com", ["Invalid email address."]),
            ("new@example.com", None),
            ("dummy2@example.com", ["Such email is already registered."]),
            (
                "a" * 129,
                [
                    "Field must be between 1 and 128 characters long.",
                    "Invalid email address.",
                ],
            ),
        ],
    )
    def test_email(
        self,
        mocker: MockFixture,
        app_for_forms,
        user_factory,
        db_session,
        registered_user,
        email: str,
        errors: list[str],
    ):
        # given
        mocker.patch.object(forms, "get_session", return_value=db_session)
        another_user = user_factory.build(
            id=2,
            email="dummy2@example.com",
        )
        db_session.add(another_user)
        db_session.commit()

        # when
        with app_for_forms.test_client(user=registered_user) as client:
            client.get("/")
            form = forms.ChangeEmailForm(
                data={
                    "password": "Clickj@cking1",
                    "email": email,
                }
            )

            # then
            is_valid = errors is None
            assert is_valid == form.validate()
            expected_errors = {} if errors is None else {"email": errors}
            assert form.errors == expected_errors
