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
        from flask_login import LoginManager

        return LoginManager()


extensions_manager = Extensions()
