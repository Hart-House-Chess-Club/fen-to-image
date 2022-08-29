from pathlib import Path

import chess

import fentoimage.boardgen as fti

FORCEGEN = False
SIZES = [16, 32, 64, 128, 256]


def pieces():
    for color in chess.COLORS:
        for piecetype in chess.PIECE_TYPES:
            yield chess.Piece(piecetype, color)


def generate_cache(cell_size: int, theme: str):
    print(f'generating pieces of size {cell_size} with theme "{theme}"...')
    cachepath = Path(__file__).parent.parent / "src" / "fentoimage" / "assets" / "cache"
    config = fti.Config(piece_theme=theme)
    for piece in pieces():
        psym = piece.symbol()
        if psym.islower():
            filename = "b" + psym.upper() + ".png"
        else:
            filename = "w" + psym + ".png"

        filedir = cachepath / str(theme) / str(cell_size)
        filedir.mkdir(parents=True, exist_ok=True)
        filepath = filedir / filename

        if not FORCEGEN or filepath.exists():
            print(f"{filename} already generated.")
        else:
            image = fti.PieceImage(cell_size, config).render(piece)
            image.save(filepath)
            print(f"{filename} done.")


def main():
    themes = fti.PieceImage.list_themes()
    for theme in themes:
        for size in SIZES:
            generate_cache(size, theme)


if __name__ == "__main__":
    main()
