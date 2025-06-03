"""
Slideshow Application

Usage:
    python main.py <image_directory> [delay_seconds] [bg_color_hex]

- Press Esc or 'q' to exit.
- Optionally specify a background color as a hex string (e.g. #222222).
- Logs to both console and logs/slideshow.log.
"""

import logging
import os
import sys
from typing import List, Tuple

from .image_utils import get_image_paths
from .slideshow import Slideshow

__all__ = [
    "TARGET_WIDTH",
    "TARGET_HEIGHT",
    "BACKGROUND_COLOR",
    "get_image_paths",
    "slideshow",
]

# --- Constants ---
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1020
BACKGROUND_COLOR = (0, 0, 0)


def slideshow(
    image_dir: str, delay: int = 3, bg_color: Tuple[int, int, int] = (0, 0, 0)
) -> None:
    """Entry point for running the slideshow from a directory."""
    try:
        image_paths = get_image_paths(image_dir)
        logging.info("Found %d images in directory: %s", len(image_paths), image_dir)
        slideshow_obj = Slideshow(image_paths, delay, bg_color)
        slideshow_obj.start()
    except FileNotFoundError:
        logging.error("Directory not found: %s", image_dir)
        return


def parse_hex_color(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    if len(hex_color) != 6 or not all(c in "0123456789abcdefABCDEF" for c in hex_color):
        raise ValueError(f"Invalid hex color: {hex_color}")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def main() -> None:
    # Improved logging: log to file daily as well as console, keep 90 days
    log_handlers: List[logging.Handler] = [logging.StreamHandler()]
    try:
        from logging.handlers import TimedRotatingFileHandler

        os.makedirs("logs", exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            "logs/slideshow.log",
            when="midnight",
            interval=1,
            backupCount=90,
            encoding="utf-8",
            utc=False,
        )
        file_handler.suffix = "%Y-%m-%d"
        log_handlers.append(file_handler)
    except Exception:
        pass
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        handlers=log_handlers,
    )
    if len(sys.argv) < 2:
        sys.exit(
            "Usage: python slideshow.py <image_directory> [delay_seconds] "
            "[bg_color_hex]"
        )
    image_dir = sys.argv[1]
    delay = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    # Optional: allow background color as hex string, e.g. "#ff0000"
    if len(sys.argv) > 3:
        try:
            bg_color = parse_hex_color(sys.argv[3])
        except Exception as e:
            sys.exit("Invalid background color: %s" % e)
    else:
        bg_color = (0, 0, 0)
    try:
        slideshow(image_dir, delay, bg_color)
    except KeyboardInterrupt:
        logging.info("Slideshow exited by user.")


if __name__ == "__main__":
    main()
