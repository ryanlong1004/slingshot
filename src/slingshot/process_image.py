from PIL import Image
from typing import Tuple


def process_image(
    path: str, size: Tuple[int, int], bg_color: Tuple[int, int, int] = (0, 0, 0)
) -> Image.Image:
    """Open, convert, resize, and center an image on a background."""
    img = Image.open(path).convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)
    background = Image.new("RGB", size, bg_color)
    offset_x = (size[0] - img.width) // 2
    offset_y = (size[1] - img.height) // 2
    background.paste(img, (offset_x, offset_y))
    return background
