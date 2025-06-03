from itertools import cycle
import logging
import traceback
from tkinter import Label, Tk
from typing import List, Tuple
from PIL import ImageTk
from process_image import process_image


class Slideshow:
    """Tkinter-based image slideshow."""

    def __init__(
        self,
        image_paths: List[str],
        delay: int = 3,
        bg_color: Tuple[int, int, int] = (0, 0, 0),
    ):
        self.image_paths = image_paths
        self.delay = delay
        self.bg_color = bg_color
        self.root: Tk | None = None
        self.label: Label | None = None
        self.screen_width: int = 0
        self.screen_height: int = 0
        self.image_cycle = cycle(self.image_paths)

    def create_window(self):
        root = Tk()
        root.title("Slideshow")
        root.attributes("-fullscreen", True)
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        label = Label(root)
        label.pack(expand=True, fill="both")

        def _exit(event=None):
            root.destroy()

        root.bind("<Escape>", _exit)
        root.bind("q", _exit)
        root.bind("Q", _exit)
        self.root = root
        self.label = label

    def update_image(self):
        if self.root is None or self.label is None:
            logging.error("Tkinter root or label not initialized.")
            return
        try:
            image_path = next(self.image_cycle)
            logging.info("Displaying image: %s", image_path)
            img = process_image(
                image_path, (self.screen_width, self.screen_height), self.bg_color
            )
            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            setattr(self.label, "photo_ref", photo)
            self.root.after(self.delay * 1000, self.update_image)
        except OSError as e:
            logging.error("Error displaying image: %s", e)
            traceback.print_exc()
            self.root.destroy()

    def start(self):
        if not self.image_paths:
            logging.warning("No images found in the specified directory.")
            return
        self.create_window()
        logging.info("Slideshow started in fullscreen mode.")
        self.update_image()
        if self.root:
            self.root.mainloop()
