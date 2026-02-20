"""Character classification and Unicode-to-ASCII normalization."""

# Unicode -> ASCII normalization map
NORMALIZATION_MAP: dict[str, str] = {
    # Arrows
    "\u2192": "->",   # →
    "\u2190": "<-",   # ←
    "\u2191": "^",    # ↑
    "\u2193": "v",    # ↓
    "\u25b6": ">",    # ▶
    "\u25c0": "<",    # ◀
    "\u27f6": "-->",  # ⟶
    "\u27f5": "<--",  # ⟵
    "\u21d2": "=>",   # ⇒
    "\u21d0": "<=",   # ⇐
    "\u25bc": "v",    # ▼
    "\u25b2": "^",    # ▲
    # Box-drawing corners
    "\u250c": "+",  # ┌
    "\u2510": "+",  # ┐
    "\u2514": "+",  # └
    "\u2518": "+",  # ┘
    "\u251c": "+",  # ├
    "\u2524": "+",  # ┤
    "\u252c": "+",  # ┬
    "\u2534": "+",  # ┴
    "\u253c": "+",  # ┼
    # Box-drawing lines
    "\u2500": "-",  # ─
    "\u2502": "|",  # │
    # Double box-drawing
    "\u2554": "+",  # ╔
    "\u2557": "+",  # ╗
    "\u255a": "+",  # ╚
    "\u255d": "+",  # ╝
    "\u2560": "+",  # ╠
    "\u2563": "+",  # ╣
    "\u2566": "+",  # ╦
    "\u2569": "+",  # ╩
    "\u256c": "+",  # ╬
    "\u2550": "=",  # ═
    "\u2551": "|",  # ║
    # Rounded corners
    "\u256d": "+",  # ╭
    "\u256e": "+",  # ╮
    "\u2570": "+",  # ╰
    "\u256f": "+",  # ╯
    # Heavy box-drawing
    "\u250f": "+",  # ┏
    "\u2513": "+",  # ┓
    "\u2517": "+",  # ┗
    "\u251b": "+",  # ┛
    "\u2503": "|",  # ┃
    "\u2501": "-",  # ━
}

CORNER_CHARS = set("┌┐└┘├┤┬┴┼╔╗╚╝╠╣╦╩╬╭╮╰╯┏┓┗┛+")
HORIZONTAL_FILL_CHARS = set("─━═-")
VERTICAL_BORDER_CHARS = set("│║┃|")


def normalize_string(s: str) -> str:
    """Replace Unicode box-drawing and arrow chars with ASCII equivalents."""
    result: list[str] = []
    for ch in s:
        result.append(NORMALIZATION_MAP.get(ch, ch))
    return "".join(result)


def is_vertical_border_char(char: str) -> bool:
    """Check if a character is a vertical border character."""
    return char in VERTICAL_BORDER_CHARS
