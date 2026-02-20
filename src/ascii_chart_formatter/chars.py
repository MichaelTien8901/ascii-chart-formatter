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
    # Mixed-weight box-drawing (light/double combinations)
    "\u2552": "+",  # ╒
    "\u2555": "+",  # ╕
    "\u2558": "+",  # ╘
    "\u255b": "+",  # ╛
    "\u2553": "+",  # ╓
    "\u2556": "+",  # ╖
    "\u2559": "+",  # ╙
    "\u255c": "+",  # ╜
    "\u255e": "+",  # ╞
    "\u2561": "+",  # ╡
    "\u2564": "+",  # ╤
    "\u2567": "+",  # ╧
    "\u256a": "+",  # ╪
    "\u255f": "+",  # ╟
    "\u2562": "+",  # ╢
    "\u2565": "+",  # ╥
    "\u2568": "+",  # ╨
    "\u256b": "+",  # ╫
    # Mixed-weight box-drawing (light/heavy combinations)
    "\u250d": "+",  # ┍
    "\u250e": "+",  # ┎
    "\u2511": "+",  # ┑
    "\u2512": "+",  # ┒
    "\u2515": "+",  # ┕
    "\u2516": "+",  # ┖
    "\u2519": "+",  # ┙
    "\u251a": "+",  # ┚
    "\u251d": "+",  # ┝
    "\u251e": "+",  # ┞
    "\u251f": "+",  # ┟
    "\u2520": "+",  # ┠
    "\u2521": "+",  # ┡
    "\u2522": "+",  # ┢
    "\u2525": "+",  # ┥
    "\u2526": "+",  # ┦
    "\u2527": "+",  # ┧
    "\u2528": "+",  # ┨
    "\u2529": "+",  # ┩
    "\u252a": "+",  # ┪
    "\u252d": "+",  # ┭
    "\u252e": "+",  # ┮
    "\u252f": "+",  # ┯
    "\u2530": "+",  # ┰
    "\u2531": "+",  # ┱
    "\u2532": "+",  # ┲
    "\u2535": "+",  # ┵
    "\u2536": "+",  # ┶
    "\u2537": "+",  # ┷
    "\u2538": "+",  # ┸
    "\u2539": "+",  # ┹
    "\u253a": "+",  # ┺
    "\u253d": "+",  # ┽
    "\u253e": "+",  # ┾
    "\u253f": "+",  # ┿
    # Dashed horizontal lines
    "\u2504": "-",  # ┄ (light triple dash)
    "\u2505": "-",  # ┅ (heavy triple dash)
    "\u2508": "-",  # ┈ (light quadruple dash)
    "\u2509": "-",  # ┉ (heavy quadruple dash)
    # Dashed vertical lines
    "\u2506": "|",  # ┆ (light triple dash vertical)
    "\u2507": "|",  # ┇ (heavy triple dash vertical)
    "\u250a": "|",  # ┊ (light quadruple dash vertical)
    "\u250b": "|",  # ┋ (heavy quadruple dash vertical)
}

CORNER_CHARS = set("┌┐└┘├┤┬┴┼╔╗╚╝╠╣╦╩╬╭╮╰╯┏┓┗┛+"
                   "╒╕╘╛╓╖╙╜╞╡╤╧╪╟╢╥╨╫"
                   "┍┎┑┒┕┖┙┚┝┞┟┠┡┢┥┦┧┨┩┪┭┮┯┰┱┲┵┶┷┸┹┺┽┾┿")
HORIZONTAL_FILL_CHARS = set("─━═-┄┅┈┉")
VERTICAL_BORDER_CHARS = set("│║┃|┆┇┊┋")


def normalize_string(s: str) -> str:
    """Replace Unicode box-drawing and arrow chars with ASCII equivalents."""
    result: list[str] = []
    for ch in s:
        result.append(NORMALIZATION_MAP.get(ch, ch))
    return "".join(result)


def is_vertical_border_char(char: str) -> bool:
    """Check if a character is a vertical border character."""
    return char in VERTICAL_BORDER_CHARS
