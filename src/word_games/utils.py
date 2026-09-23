from datetime import datetime
from zoneinfo import ZoneInfo


TZ_UTC = ZoneInfo("UTC")


def rename_dict_key(dictionary, old_key, new_key):
    if old_key in dictionary:
        dictionary[new_key] = dictionary.pop(old_key)


def normalize_text(text: str) -> str:
    return text.strip().title().replace("_", " ")


def to_user_timezone(dt: datetime, timezone: str):
    return dt.astimezone(ZoneInfo(timezone))


def section_sort_key(value: str):
    """Return soorting key for classic section pattern <section>.<subsection>"""
    return tuple(map(int, value.split(".")))


def raise_if_nonpositive_int(value: int):
    if value <= 0:
        msg = "value must be positive"
        raise ValueError(msg)


def raise_if_negative_int(value: int):
    if value < 0:
        msg = "value must be nonnegative"
        raise ValueError(msg)


# TODO: implement url_has_allowed_host_and_scheme: https://github.com/django/django/blob/4.0/django/utils/http.py#L239  # noqa: FIX002
