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
import traceback
from itertools import cycle
from tkinter import Label, Tk
from typing import List, Tuple

try:
    from PIL import Image, ImageTk
except ImportError:
    sys.exit("Pillow is required. Install with: pip install pillow")

__all__ = [
    "TARGET_WIDTH",
    "TARGET_HEIGHT",
    "BACKGROUND_COLOR",
    "IMAGE_EXTENSIONS",
    "get_image_paths",
    "process_image",
    "create_slideshow_window",
    "run_slideshow",
    "slideshow",
]

# --- Constants ---
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1020
BACKGROUND_COLOR = (0, 0, 0)
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp")


def get_image_paths(image_dir: str) -> List[str]:
    """Return a list of image file paths in the directory."""
    return [
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ]


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


def create_slideshow_window() -> Tuple[Tk, Label, int, int]:
    """Create and return a fullscreen Tkinter window, image label, and screen size."""
    root = Tk()
    root.title("Slideshow")
    root.attributes("-fullscreen", True)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    label = Label(root)
    label.pack(expand=True, fill="both")

    # Bind Esc and 'q' to exit
    def _exit(event=None):
        root.destroy()

    root.bind("<Escape>", _exit)
    root.bind("q", _exit)
    root.bind("Q", _exit)
    return root, label, screen_width, screen_height


def run_slideshow(
    image_paths: List[str], delay: int = 3, bg_color: Tuple[int, int, int] = (0, 0, 0)
) -> None:
    """Run the Tkinter slideshow for the given image paths."""
    if not image_paths:
        logging.warning("No images found in the specified directory.")
        return
    root, label, screen_width, screen_height = create_slideshow_window()
    image_cycle = cycle(image_paths)

    def update_image() -> None:
        try:
            image_path = next(image_cycle)
            logging.info("Displaying image: %s", image_path)
            img = process_image(image_path, (screen_width, screen_height), bg_color)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo  # Tkinter reference
            root.after(delay * 1000, update_image)
        except Exception as e:
            logging.error("Error displaying image: %s", e)
            traceback.print_exc()
            root.destroy()

    logging.info("Slideshow started in fullscreen mode.")
    update_image()
    root.mainloop()


def slideshow(
    image_dir: str, delay: int = 3, bg_color: Tuple[int, int, int] = (0, 0, 0)
) -> None:
    """Entry point for running the slideshow from a directory."""
    try:
        image_paths = get_image_paths(image_dir)
        logging.info("Found %d images in directory: %s", len(image_paths), image_dir)
        run_slideshow(image_paths, delay, bg_color)
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
