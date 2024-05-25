import re


_pascal_case_delimiter = re.compile(r"(?<=[a-z])(?=[A-Z])")


def to_snake_case(identifier: str) -> str:
    return "_".join(word.lower() for word in _pascal_case_delimiter.split(identifier))
