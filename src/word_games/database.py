import re

from sqlalchemy.orm import DeclarativeBase, declared_attr


camel_case_to_snake_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_case_to_snake_case(text: str) -> str:
    return camel_case_to_snake_case_pattern.sub("_", text).lower()


class BaseTable(DeclarativeBase):
    """All SQLAlchemy tables should inherit from this class."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        name_without_table = cls.__name__.replace("Table", "")
        return camel_case_to_snake_case(name_without_table)
