import subprocess
from dataclasses import dataclass
from pathlib import Path
from subprocess import Popen
from typing import Tuple

import chess
from chess import Board, Piece
from PIL import Image, ImageDraw, ImageFont


@dataclass
class Config:
    inkscape_location: str = "inkscape"
    piece_theme: str = "cburnett"
    light_square_color: Tuple[int, int, int] = (240, 217, 181)
    dark_square_color: Tuple[int, int, int] = (181, 136, 99)
    light_text_color: Tuple[int, int, int] = (240, 217, 181)
    dark_text_color: Tuple[int, int, int] = (148, 111, 81)


class PieceImage:
    PIECE_LOCATION = Path(__file__).parent / "pieces-svg"

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
    def __init__(self, fen: str, config: Config):
        self.board = Board(fen)
        self.config = config

    def render(self, size: int = 1024):
        if size % 8 != 0:
            raise RuntimeError("Size must be multiple of 8")

        cell_size = int(size / 8)
        piece_drawer = PieceImage(cell_size, self.config)
        image = Image.new(mode="RGB", size=(size, size))
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype("./NotoSans-Bold.ttf", 24)
        htext = "abcdefgh"
        vtext = "87654321"
        text_colors = [self.config.light_text_color, self.config.dark_text_color]

        colors = [self.config.light_square_color, self.config.dark_square_color]

        for x in range(8):
            for y in range(8):
                rectx = x * cell_size
                recty = y * cell_size

                # step 1: render cell
                draw.rectangle(
                    (rectx, recty, rectx + cell_size, recty + cell_size),
                    fill=colors[(x + y) % 2],
                )

                # step 2: render cell location
                if y == 7:
                    draw.text(
                        (rectx + 8, recty + cell_size - 8),
                        htext[x],
                        fill=text_colors[x % 2],
                        anchor="ls",
                        font=font,
                    )

                if x == 7:
                    draw.text(
                        (rectx + cell_size - 8, recty + 8),
                        vtext[y],
                        fill=text_colors[y % 2],
                        anchor="rt",
                        font=font,
                    )

                # step 3: render piece
                # since chess.SQUARES starts at a1
                square = chess.SQUARES[x + (7 - y) * 8]
                piece = self.board.piece_at(square)
                if piece is not None:
                    piece_image = piece_drawer.render(piece)
                    image.paste(piece_image, (rectx, recty), piece_image)

        return image


if __name__ == "__main__":
    fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    image = FenToImage(fen, Config()).render()
    image.show()
