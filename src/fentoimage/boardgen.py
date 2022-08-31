import subprocess
from dataclasses import dataclass
from pathlib import Path
from subprocess import Popen

import chess
from chess import Board, Piece
from PIL import Image, ImageDraw, ImageFont


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
    square: SquareConfig = SquareConfig()
    text: TextConfig = TextConfig()


class PieceImage:
    PIECE_LOCATION = Path(__file__).parent / "assets" / "pieces"

    def __init__(self, size: int, config: Config) -> None:
        self.size = size
        self.config = config
        self.cache = {}

        if self.config.piece_theme not in self.list_themes():
            raise RuntimeError(
                f'Piece theme "{self.config.piece_theme}" does not exist.'
            )

    @classmethod
    def list_themes(cls):
        return [p.name for p in cls.PIECE_LOCATION.iterdir() if p.is_dir()]

    def piece_to_filename(self, piece: Piece) -> Path:
        psym = piece.symbol()
        if psym.islower():
            file = "b" + psym.upper() + ".svg"
        else:
            file = "w" + psym + ".svg"
        return self.PIECE_LOCATION / self.config.piece_theme / file

    def render(self, piece: Piece):
        psym = piece.symbol()
        if psym in self.cache:
            return self.cache[psym]

        inkscape_proc = Popen(
            [
                self.config.inkscape_location,
                self.piece_to_filename(piece),
                "-w",
                str(self.size),
                "--export-type",
                "png",
                "-o",
                "-",
            ],
            stdout=subprocess.PIPE,
        )
        rcode = inkscape_proc.wait()
        if rcode != 0:
            raise RuntimeError("inkscape app error")
        else:
            if inkscape_proc.stdout is not None:
                piece_image = Image.open(inkscape_proc.stdout, formats=["png"])
                self.cache[psym] = piece_image
                return piece_image
            else:
                raise RuntimeError("inkscape file error")


class FenToImage:
    def __init__(self, fen: str, config: Config = Config(), cell_size: int = 128):
        self.board = Board(fen)
        self.cell_size = cell_size
        self.config = config
        self.text_config = config.text
        self.square_config = config.square

        self.piece_drawer = PieceImage(self.cell_size, self.config)
        self.font = ImageFont.truetype(
            str(Path(__file__).parent / "assets" / "NotoSans-Bold.ttf"),
            self.text_config.font_size,
        )

    def _init_image(self):
        size = self.cell_size * 8
        self.image = Image.new(mode="RGB", size=(size, size))
        self.draw = ImageDraw.Draw(self.image)

    def _render_square_background(self, x, y):
        rectx = x * self.cell_size
        recty = y * self.cell_size
        colors = self.square_config.color

        self.draw.rectangle(
            (rectx, recty, rectx + self.cell_size, recty + self.cell_size),
            fill=colors[(x + y) % 2],
        )

    def _render_square_location(self, x, y):
        rectx = x * self.cell_size
        recty = y * self.cell_size

        htext = "abcdefgh"
        vtext = "87654321"
        text_colors = self.text_config.color
        text_padding = self.text_config.padding

        if y == 7:
            self.draw.text(
                (rectx + text_padding, recty + self.cell_size - text_padding),
                htext[x],
                fill=text_colors[x % 2],
                anchor="ls",
                font=self.font,
            )

        if x == 7:
            self.draw.text(
                (rectx + self.cell_size - text_padding, recty + text_padding),
                vtext[y],
                fill=text_colors[y % 2],
                anchor="rt",
                font=self.font,
            )

    def _render_piece(self, x, y):
        rectx = x * self.cell_size
        recty = y * self.cell_size

        # since chess.SQUARES starts at a1
        square = chess.SQUARES[x + (7 - y) * 8]
        piece = self.board.piece_at(square)
        if piece is not None:
            piece_image = self.piece_drawer.render(piece)
            self.image.paste(piece_image, (rectx, recty), piece_image)

    def render(self):
        self._init_image()

        for x in range(8):
            for y in range(8):
                self._render_square_background(x, y)
                if self.text_config.enabled:
                    self._render_square_location(x, y)
                self._render_piece(x, y)

        return self.image


if __name__ == "__main__":
    fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    image = FenToImage(fen, Config()).render()
    image.show()
