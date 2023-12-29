# fen-to-image

Generate a chess board image given a FEN, à la Lichess style. 

## Installation

fentoimage is available on [PyPI](https://pypi.org/project/fentoimage/).

```sh
pip install fentoimage
```

## Example Usage

```python
import chess

from fentoimage.board import BoardImage

fen = "rnbqk1nr/pppp1ppp/8/4p3/1bP5/2N5/PP1PPPPP/R1BQKBNR w KQkq - 2 3"
renderer = BoardImage(fen)
image = renderer.render(highlighted_squares=(chess.F8, chess.B4))
image.show()
```

## Example Output

With default alignment and default white at the bottom

<p align="center">
  <img src="https://user-images.githubusercontent.com/36672196/187807385-6087105e-bf99-4167-8a75-7fb76b66a49f.PNG" width="512" alt="English Opening: King's English Variation, Kramnik-Shirov Counterattack">
</p>


With black at the bottom

