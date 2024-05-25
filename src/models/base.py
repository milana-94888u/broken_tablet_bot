from typing import Any

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import JSON

from utils.name_utils import to_snake_case


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSON,
    }

    @declared_attr.directive
    def __tablename__(cls: type) -> str:
        return to_snake_case(cls.__name__)
