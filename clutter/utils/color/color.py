from .misc import esc as c
from .misc import make_color as s

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


FG_END = c(39)
BG_END = c(49)
HL_END = c(22, 27, 39)

black = s(c(30), FG_END)
red = s(c(31), FG_END)
green = s(c(32), FG_END)
yellow = s(c(33), FG_END)
blue = s(c(34), FG_END)
magenta = s(c(35), FG_END)
cyan = s(c(36), FG_END)
white = s(c(37), FG_END)

black_bg = s(c(40), BG_END)
red_bg = s(c(41), BG_END)
green_bg = s(c(42), BG_END)
yellow_bg = s(c(43), BG_END)
blue_bg = s(c(44), BG_END)
magenta_bg = s(c(45), BG_END)
cyan_bg = s(c(46), BG_END)
white_bg = s(c(47), BG_END)

black_hl = s(c(1, 30, 7), HL_END)
red_hl = s(c(1, 31, 7), HL_END)
green_hl = s(c(1, 32, 7), HL_END)
yellow_hl = s(c(1, 33, 7), HL_END)
blue_hl = s(c(1, 34, 7), HL_END)
magenta_hl = s(c(1, 35, 7), HL_END)
cyan_hl = s(c(1, 36, 7), HL_END)
white_hl = s(c(1, 37, 7), HL_END)

bold = s(c(1), c(22))
italic = s(c(3), c(23))
underline = s(c(4), c(24))
strike = s(c(9), c(29))
blink = s(c(5), c(25))
