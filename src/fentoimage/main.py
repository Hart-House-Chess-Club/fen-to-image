import chess

from board import BoardImage
from config import Config

if __name__ == "__main__":
    print("Hello World")

    fen = "rnbqk1nr/pppp1ppp/8/4p3/1bP5/2N5/PP1PPPPP/R1BQKBNR b KQkq - 2 3"

    config = Config(piece_theme="fantasy", flipBoard=True)

    renderer = BoardImage(fen, config=config)
    image = renderer.render(highlighted_squares=(chess.F8, chess.B4))
    image.show()
