import subprocess
from pathlib import Path
from subprocess import Popen

from chess import Piece
from PIL import Image

from config import Config


class PieceImage:
    PIECE_LOCATION = Path(__file__).parent / "assets" / "pieces"
    CACHE_LOCATION = Path(__file__).parent / "assets" / "cache"

    def __init__(self, size: int, config: Config) -> None:
        self.size = size
        self.config = config
        self.cache: dict[str, Image.Image] = {}

        if self.config.piece_theme not in self.list_themes():
            raise RuntimeError(f'Piece theme "{self.config.piece_theme}" does not exist.')

    @classmethod
    def list_themes(cls):
        return [p.name for p in cls.PIECE_LOCATION.iterdir() if p.is_dir()]

    def piece_to_filename(self, piece: Piece, extension: str = ""):
        psym = piece.symbol()
        if psym.islower():
            return "b" + psym.upper() + extension
        else:
            return "w" + psym + extension

    def get_piece_from_cache(self, piece: Piece):
        psym = piece.symbol()
        if psym in self.cache:
            return self.cache[psym]
        file = self.piece_to_filename(piece, ".png")
        filepath = self.CACHE_LOCATION / self.config.piece_theme / str(self.size) / file
        if filepath.exists():
            return Image.open(filepath, formats=["png"])

    def render(self, piece: Piece):
        cached_image = self.get_piece_from_cache(piece)
        if cached_image:
            return cached_image

        file = self.piece_to_filename(piece, ".svg")
        filepath = self.PIECE_LOCATION / self.config.piece_theme / file
        inkscape_proc = Popen(
            [
                self.config.inkscape_location,
                filepath,
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
                self.cache[piece.symbol()] = piece_image
                return piece_image
            else:
                raise RuntimeError("inkscape file error")
