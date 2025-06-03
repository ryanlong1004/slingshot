import os
from typing import List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query

from .image_utils import get_image_paths
from .slideshow import Slideshow
from .utils import parse_hex_color

app = FastAPI(title="Slingshot Slideshow API")

slideshow_status = {"running": False}


def run_slideshow_bg(image_paths, delay, bg_tuple):
    slideshow_status["running"] = True
    try:
        slideshow = Slideshow(image_paths, delay, bg_tuple)
        slideshow.start()
    finally:
        slideshow_status["running"] = False


@app.get(
    "/images",
    response_model=List[str],
)
def list_images(
    directory: str = Query(..., description="Directory to list images from"),
):
    """List all images in a directory."""
    if not os.path.isdir(directory):
        raise HTTPException(status_code=404, detail="Directory not found")
    return get_image_paths(directory)


@app.post(
    "/slideshow/start",
)
def start_slideshow(
    background_tasks: BackgroundTasks,
    directory: str = Query(..., description="Directory containing images"),
    delay: int = Query(3, ge=1, le=60, description="Delay between images in seconds"),
    bg_color: Optional[str] = Query(
        None, description="Background color as hex string, e.g. #222222"
    ),
):
    """Start a slideshow (non-blocking)."""
    if not os.path.isdir(directory):
        raise HTTPException(status_code=404, detail="Directory not found")
    image_paths = get_image_paths(directory)
    if not image_paths:
        raise HTTPException(status_code=404, detail="No images found")
    if bg_color:
        try:
            bg_tuple = parse_hex_color(bg_color)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid color: {e}") from e
    else:
        bg_tuple = (0, 0, 0)
    if slideshow_status["running"]:
        raise HTTPException(status_code=409, detail="Slideshow already running")
    background_tasks.add_task(run_slideshow_bg, image_paths, delay, bg_tuple)
    return {"status": "slideshow started"}


@app.get("/slideshow/status")
def get_status():
    """Get the status of the slideshow."""
    return {"running": slideshow_status["running"]}
