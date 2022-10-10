"""画像切り取り範囲モジュール.
"""


class Crop:
    """clipping class."""

    def __init__(self, top: int, left: int, right: int, bottom: int) -> None:
        """constructor.

        Args:
            top: Upper cropping area ratio.
            left: Left cropping area ratio.
            right: Right cropping area ratio.
            bottom: Lower crop area ratio.
        """
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    @classmethod
    def from_dict(cls, init_data) -> 'Crop':
        return cls(
            init_data.get('top', 0),
            init_data.get('left', 0),
            init_data.get('right', 0),
            init_data.get('bottom', 0),
        )

    def __str__(self) -> str:
        return f'change to [top {self.top}, left {self.left}, right {self.right}, bottom {self.bottom}]'

    def to_dict(self) -> dict:
        return {
            'top': self.top,
            'left': self.left,
            'right': self.right,
            'bottom': self.bottom,
        }
