from enum import IntEnum
from typing import Final

from wtforms.validators import Length


EMAIL_LENGTH = Length(1, 128)
USERNAME_LENGTH = Length(4, 32)
PASSWORD_LENGTH = Length(12, 64)


TOKEN_EXP_TIME_SEC: Final[int] = 3600
ENCODING: Final[str] = "utf-8"


class HTTPStatusCode(IntEnum):
    OK = 200
    NO_CONTENT = 204

    BAD_REQUEST = 400
    FORBIDDEN = 403
