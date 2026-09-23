from functools import cached_property


class Extensions:
    @cached_property
    def mail(self):
        from flask_mail import Mail

        return Mail()

    @cached_property
    def csrf(self):
        from flask_wtf.csrf import CSRFProtect

        return CSRFProtect()

    @cached_property
    def login_manager(self):
        from flask_login import AnonymousUserMixin, LoginManager

        class MyAnonymousUser(AnonymousUserMixin):
            role = None

        login_manager = LoginManager()
        login_manager.anonymous_user = MyAnonymousUser
        return login_manager


extensions_manager = Extensions()
