import colorsys
import re
from hashlib import md5
from typing import Optional


def to_id(string: Optional[str]) -> str:
    """Convert a string to an ID."""
    if string is None:
        return ""
    return (re.sub(r"[^A-Za-z0-9]", "", string)).lower()


def HSLToRGB(H: float, S: float, L: float) -> tuple:
    """Convert HSL to RGB."""
    H /= 360
    S /= 100
    L /= 100
    R, G, B = colorsys.hls_to_rgb(H, L, S)
    return R, G, B


def username_color(name: str) -> tuple:
    """Get the color of a username."""
    name = to_id(name)
    hash = md5(name.encode()).hexdigest()
    H = int(hash[4:8], 16) % 360
    S = int(hash[0:4], 16) % 50 + 40
    L = int(hash[8:12], 16) % 20 + 30
    R, G, B = HSLToRGB(H, S, L)
    lum = R * R * R * 0.2126 + G * G * G * 0.7152 + B * B * B * 0.0722
    HLmod = (lum - 0.2) * -150
    if HLmod > 18:
        HLmod = (HLmod - 18) * 2.5
    elif HLmod < 0:
        HLmod = (HLmod - 0) / 3
    else:
        HLmod = 0
    Hdist = min(abs(180 - H), abs(240 - H))
    if Hdist < 15:
        HLmod += (15 - Hdist) / 3
    L += HLmod
    return H, S, L
