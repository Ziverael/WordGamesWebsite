from typing import Final

from wtforms.validators import Length


EMAIL_LENGTH = Length(1, 128)
USERNAME_LENGTH = Length(4, 32)
PASSWORD_LENGTH = Length(12, 64)


TOKEN_EXP_TIME_SEC: Final[int] = 3600
ENCODING: Final[str] = "utf-8"
