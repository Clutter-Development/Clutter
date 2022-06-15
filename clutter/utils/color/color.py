from .misc import esc as e
from .misc import make_color as m

__all__ = (
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "black_bg",
    "red_bg",
    "green_bg",
    "yellow_bg",
    "blue_bg",
    "magenta_bg",
    "cyan_bg",
    "white_bg",
    "black_hl",
    "red_hl",
    "green_hl",
    "yellow_hl",
    "blue_hl",
    "magenta_hl",
    "cyan_hl",
    "white_hl",
    "bold",
    "italic",
    "underline",
    "strike",
    "blink",
)


FG_END = e(39)

black = m(e(30), FG_END)
red = m(e(31), FG_END)
green = m(e(32), FG_END)
yellow = m(e(33), FG_END)
blue = m(e(34), FG_END)
magenta = m(e(35), FG_END)
cyan = m(e(36), FG_END)
white = m(e(37), FG_END)

BG_END = e(49)

black_bg = m(e(40), BG_END)
red_bg = m(e(41), BG_END)
green_bg = m(e(42), BG_END)
yellow_bg = m(e(43), BG_END)
blue_bg = m(e(44), BG_END)
magenta_bg = m(e(45), BG_END)
cyan_bg = m(e(46), BG_END)
white_bg = m(e(47), BG_END)

HL_END = e(22, 27, 39)

black_hl = m(e(1, 30, 7), HL_END)
red_hl = m(e(1, 31, 7), HL_END)
green_hl = m(e(1, 32, 7), HL_END)
yellow_hl = m(e(1, 33, 7), HL_END)
blue_hl = m(e(1, 34, 7), HL_END)
magenta_hl = m(e(1, 35, 7), HL_END)
cyan_hl = m(e(1, 36, 7), HL_END)
white_hl = m(e(1, 37, 7), HL_END)

bold = m(e(1), e(22))
italic = m(e(3), e(23))
underline = m(e(4), e(24))
strike = m(e(9), e(29))
blink = m(e(5), e(25))
