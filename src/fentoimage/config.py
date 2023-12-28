from dataclasses import dataclass

@dataclass
class SquareConfig:
    light_color: tuple[int, int, int] = (240, 217, 181)
    dark_color: tuple[int, int, int] = (181, 136, 99)
    light_highlight_color: tuple[int, int, int] = (205, 210, 106)
    dark_highlight_color: tuple[int, int, int] = (170, 162, 58)

    @property
    def color(self):
        return (self.light_color, self.dark_color)

    @property
    def highlight_color(self):
        return (self.light_highlight_color, self.dark_highlight_color)


@dataclass
class TextConfig:
    enabled: bool = True
    light_color: tuple[int, int, int] = (240, 217, 181)
    dark_color: tuple[int, int, int] = (148, 111, 81)
    font_size: int = 24
    padding: int = 8

    @property
    def color(self):
        return (self.light_color, self.dark_color)


@dataclass
class Config:
    inkscape_location: str = "inkscape"
    piece_theme: str = "cburnett"
    flip_board: bool = True
    square: SquareConfig = SquareConfig()
    text: TextConfig = TextConfig()
