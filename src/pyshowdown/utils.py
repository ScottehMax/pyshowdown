import re

from typing import Optional


def to_id(string: Optional[str]) -> str:
    """Convert a string to an ID."""
    if string is None:
        return ""
    return (re.sub(r"[^A-Za-z0-9]", "", string)).lower()
