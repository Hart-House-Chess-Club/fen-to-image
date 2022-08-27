import subprocess
from dataclasses import dataclass
from subprocess import Popen

import chess
from chess import Board, Piece
from PIL import Image, ImageDraw


@dataclass
class Config:
    inkscape_location: str = "inkscape"
    piece_theme: str = "cburnett"


class PieceImage:
    def __init__(self, size: int, config: Config) -> None:
        self.size = size
        self.config = config
        self.cache = {}

    def piece_to_filename(self, piece: Piece) -> str:
        psym = piece.symbol()
        if psym.islower():
            file = "b" + psym.upper() + ".svg"
        else:
            file = "w" + psym + ".svg"
        return f"./pieces-svg/{self.config.piece_theme}/{file}"

    def render(self, piece: Piece):
        psym = piece.symbol()
        if psym in self.cache:
            return self.cache[psym]

        svgfile = self.piece_to_filename(piece)
        inkscape_proc = Popen(
            [
                self.config.inkscape_location,
                svgfile,
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

        colors = [(240, 217, 181), (181, 136, 99)]
        for x in range(8):
            for y in range(8):
                rectx = x * cell_size
                recty = y * cell_size

                # step 1: render cell
                draw.rectangle(
                    (rectx, recty, rectx + cell_size, recty + cell_size),
                    fill=colors[(x + y) % 2],
                )

                # step 2: render piece
                square = chess.SQUARES[x + y * 8]
                piece = self.board.piece_at(square)
                if piece is not None:
                    piece_image = piece_drawer.render(piece)
                    image.paste(piece_image, (rectx, recty), piece_image)

        return image


if __name__ == "__main__":
    fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    image = FenToImage(fen, Config()).render()
    image.show()
