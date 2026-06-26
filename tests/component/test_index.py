import pytest
from flask_login import current_user


class TestIndex:
    def test_request_example(self, client, captured_templates):
        # when
        with client:
            response = client.get("/")

            # then
            assert current_user.is_anonymous
        assert response.status_code == 200
        assert response.request.path == "/"
        template, context = captured_templates[0]
        assert template.name == "index.html"
        assert context["current_user"].is_authenticated is False

    @pytest.mark.parametrize("confirmed", [True, False])
    def test_request_with_logged_in_user(
        self,
        app,
        db_session,
        captured_templates,
        user_factory,
        confirmed: bool,
    ):
        # given
        user = user_factory.build(id=1, confirmed=confirmed)
        db_session.add(user)
        db_session.commit()

        # when
        with app.test_client(user=user) as client:
            response = client.get("/")
            assert current_user.is_authenticated

        # then
        assert response.status_code == 200
        assert response.request.path == "/"
        template, context = captured_templates[0]
        assert template.name == "index.html"
        assert context["current_user"].is_authenticated is True
        assert context["current_user"].id == 1
