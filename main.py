import subprocess
from subprocess import Popen

from chess import Board, Piece
from PIL import Image


def piece_to_filename(piece: Piece, theme: str) -> str:
    psym = piece.symbol()
    if psym.islower():
        file = "b" + psym.upper() + ".svg"
    else:
        file = "w" + psym + ".svg"
    return f"./pieces-svg/{theme}/{file}"


def piece_to_image(piece: Piece, size: int = 64):
    svgfile = piece_to_filename(piece, "cburnett")
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


if __name__ == "__main__":
    image: Image.Image = piece_to_image(Piece.from_symbol("R"))
    image.save("rook-test.png")
