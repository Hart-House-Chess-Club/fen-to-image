from io import BytesIO

from chess import Board, Piece
from PIL import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


def piece_to_filename(piece: Piece, theme: str) -> str:
    psym = piece.symbol()
    if psym.islower():
        file = "b" + psym.upper() + ".svg"
    else:
        file = "w" + psym + ".svg"
    return f"./pieces-svg/{theme}/{file}"


def piece_to_image(piece: Piece, size: int = 64):
    # TODO, use inkscape cli for conversion
    svgfile = piece_to_filename(piece, "cburnett")
    drawing = svg2rlg(svgfile)
    out = BytesIO()
    renderPM.drawToFile(drawing, out, fmt="PNG", bg=)
    return Image.open(out)


class FenToImage:
    def __init__(self, fen: str):
        self.board = Board(fen)


if __name__ == "__main__":
    image: Image.Image = piece_to_image(Piece.from_symbol("R"))
    image.save("rook-test.png")
