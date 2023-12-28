from pathlib import Path

import chess
from chess import Board
from PIL import Image, ImageDraw, ImageFont

from config import Config
from piece import PieceImage


class BoardImage:
    def __init__(self, fen: str, config: Config = Config(), square_size: int = 128):
        self.flip_board = config.flip_board

        if self.flip_board:
            # here we will flip the fen
            fen = self._flip_fen(fen)

        self.board = Board(fen)
        self.square_size = square_size
        self.config = config
        self.text_config = config.text
        self.square_config = config.square

        self.piece_drawer = PieceImage(self.square_size, self.config)
        self.font = ImageFont.truetype(
            str(Path(__file__).parent / "assets" / "NotoSans-Bold.ttf"),
            self.text_config.font_size,
        )

    def _init_image(self) -> None:
        size = self.square_size * 8
        self.image = Image.new(mode="RGB", size=(size, size))
        self.draw = ImageDraw.Draw(self.image)

    def _get_square_at(self, x, y) -> int:
        # since chess.SQUARES starts at a1
        return chess.SQUARES[x + (7 - y) * 8]

    def _render_square_background(self, x, y, highlighted_squares=()) -> None:
        rectx = x * self.square_size
        recty = y * self.square_size
        colors = self.square_config.color
        highlight_colors = self.square_config.highlight_color

        fill_color = colors[(x + y) % 2]
        if self._get_square_at(x, y) in highlighted_squares:
            fill_color = highlight_colors[(x + y) % 2]

        self.draw.rectangle(
            (rectx, recty, rectx + self.square_size, recty + self.square_size),
            fill=fill_color,
        )

    def _render_square_location(self, x, y) -> None:
        rectx = x * self.square_size
        recty = y * self.square_size

        htext = "abcdefgh"
        vtext = "87654321"

        # if flip board, then reverse htext and vtext
        if self.flip_board:
            htext = htext[::-1]
            vtext = vtext[::-1]

        text_colors = self.text_config.color
        text_padding = self.text_config.padding

        if y == 7:
            self.draw.text(
                (rectx + text_padding, recty + self.square_size - text_padding),
                htext[x],
                fill=text_colors[x % 2],
                anchor="ls",
                font=self.font,
            )

        if x == 7:
            self.draw.text(
                (rectx + self.square_size - text_padding, recty + text_padding),
                vtext[y],
                fill=text_colors[y % 2],
                anchor="rt",
                font=self.font,
            )

    def _render_piece(self, x, y) -> None:
        rectx = x * self.square_size
        recty = y * self.square_size

        square = self._get_square_at(x, y)
        piece = self.board.piece_at(square)
        if piece is not None:
            piece_image = self.piece_drawer.render(piece)
            self.image.paste(piece_image, (rectx, recty), piece_image)

    def _flip_fen(self, fen) -> str:
        # get the index of the space
        space_ind = fen.index(" ")
        board_lines_fen = fen[0:space_ind]

        # get the board lines fen split up
        board_lines_fen = board_lines_fen.split("/")

        new_fen = ""

        # read board lines fen backwards for first flip
        for i in range(len(board_lines_fen) - 1, -1, -1):
            new_fen += board_lines_fen[i][::-1]

            # if not at the end, add a slash
            if i != 0:
                new_fen += "/"

        # add back the active colour, castling, en passant, half moves, full moves
        new_fen = new_fen + fen[space_ind:]

        return new_fen

    def render(self, highlighted_squares=()) -> Image:
        """
        Render the image of the board
        :param highlighted_squares: tuple representing the board values to render
        :return: returns the image that is rendered
        """
        self._init_image()

        if self.flip_board:
            # reassign highlighted_squares to be flipped along horizontal, then vertically mirrored
            highlighted_squares = ((7 - highlighted_squares[0] // 8) * 8 + (7 - highlighted_squares[0] % 8),
                                   (7 - highlighted_squares[1] // 8) * 8 + (7 - highlighted_squares[1] % 8)
                                   )

        for x in range(8):
            for y in range(8):
                self._render_square_background(x, y, highlighted_squares)
                if self.text_config.enabled:
                    self._render_square_location(x, y)
                self._render_piece(x, y)

        return self.image
