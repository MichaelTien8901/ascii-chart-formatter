"""ASCII Chart Formatter — fix misaligned right edges in ASCII-art box diagrams."""

from .chars import normalize_string
from .formatter import fix_ascii_art

__all__ = [
    "fix_ascii_art",
    "normalize_string",
]
