import re

def to_id(string: str) -> str:
    return (re.sub(r'[^A-Za-z0-9]', '', string)).lower()