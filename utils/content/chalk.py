from typing import Union, Any, Callable


def _t(b: Union[bytes, Any]) -> str:
    return b.decode() if isinstance(b, bytes) else b


def _esc(*codes: Union[int, str]) -> str:
    return _t('\x1b[{}m').format(_t(';').join(_t(str(c)) for c in codes))


def _make_color(start, end: str) -> Callable[[str], str]:
    def color_func(s: str) -> str:
        return start + _t(s) + end

    return color_func


class Chalk:
    _FG_END = _esc(39)
    _BG_END = _esc(49)
    _HL_END = _esc(22, 27, 39)

    black = _make_color(_esc(30), _FG_END)
    red = _make_color(_esc(31), _FG_END)
    green = _make_color(_esc(32), _FG_END)
    yellow = _make_color(_esc(33), _FG_END)
    blue = _make_color(_esc(34), _FG_END)
    magenta = _make_color(_esc(35), _FG_END)
    cyan = _make_color(_esc(36), _FG_END)
    white = _make_color(_esc(37), _FG_END)

    black_bg = _make_color(_esc(40), _BG_END)
    red_bg = _make_color(_esc(41), _BG_END)
    green_bg = _make_color(_esc(42), _BG_END)
    yellow_bg = _make_color(_esc(43), _BG_END)
    blue_bg = _make_color(_esc(44), _BG_END)
    magenta_bg = _make_color(_esc(45), _BG_END)
    cyan_bg = _make_color(_esc(46), _BG_END)
    white_bg = _make_color(_esc(47), _BG_END)

    black_hl = _make_color(_esc(1, 30, 7), _HL_END)
    red_hl = _make_color(_esc(1, 31, 7), _HL_END)
    green_hl = _make_color(_esc(1, 32, 7), _HL_END)
    yellow_hl = _make_color(_esc(1, 33, 7), _HL_END)
    blue_hl = _make_color(_esc(1, 34, 7), _HL_END)
    magenta_hl = _make_color(_esc(1, 35, 7), _HL_END)
    cyan_hl = _make_color(_esc(1, 36, 7), _HL_END)
    white_hl = _make_color(_esc(1, 37, 7), _HL_END)

    bold = _make_color(_esc(1), _esc(22))
    italic = _make_color(_esc(3), _esc(23))
    underline = _make_color(_esc(4), _esc(24))
    strike = _make_color(_esc(9), _esc(29))
    blink = _make_color(_esc(5), _esc(25))
