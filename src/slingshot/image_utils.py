from typing import List
import os

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp")


def get_image_paths(image_dir: str) -> List[str]:
    """Return a list of image file paths in the directory."""
    return [
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ]
