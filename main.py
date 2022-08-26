import subprocess
from dataclasses import dataclass
from subprocess import Popen

from chess import Board, Piece
from PIL import Image


@dataclass
class Config:
    inkscape_location: str = "inkscape"
    piece_theme: str = "cburnett"


class PieceImage:
    def __init__(self, piece: Piece, config: Config) -> None:
        self.piece = piece
        self.config = config

    def piece_to_filename(self) -> str:
        psym = self.piece.symbol()
        if psym.islower():
            file = "b" + psym.upper() + ".svg"
        else:
            file = "w" + psym + ".svg"
        return f"./pieces-svg/{self.config.piece_theme}/{file}"

    def render(self, size: int = 64):
        svgfile = self.piece_to_filename()
        inkscape_proc = Popen(
            ["inkscape", svgfile, "-w", str(size), "--export-type", "png", "-o", "-"],
            stdout=subprocess.PIPE,
        )
        rcode = inkscape_proc.wait()
        if rcode != 0:
            raise RuntimeError("inkscape app error")
        else:
            if inkscape_proc.stdout is not None:
                return Image.open(inkscape_proc.stdout, formats=["png"])
            else:
                raise RuntimeError("inkscape file error")


class FenToImage:
    def __init__(self, fen: str):
        self.board = Board(fen)

    def render(self):
        raise NotImplementedError


if __name__ == "__main__":
    config = Config(piece_theme="governor")
    image = PieceImage(Piece.from_symbol("R"), config).render(128)
    image.save("rook-test.png")
