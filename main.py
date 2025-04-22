"""
VLC Player Control API

A FastAPI application that provides endpoints to control VLC media player
for fullscreen video playback.
"""

from pathlib import Path
from typing import Dict, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field, validator
from fastapi.middleware.cors import CORSMiddleware

import config
import player

# Configure logger
logger = config.setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

player_manager = player.VLCPlayerManager()


class VideoRequest(BaseModel):
    """Request model for playing a video"""

    video_path: str = Field(..., description="Path to the video file")
    loop: bool = Field(True, description="Whether to loop the video")
    fullscreen: bool = Field(True, description="Whether to play in fullscreen mode")

    @classmethod
    def validate_video_path(cls, value):
        if not Path(value).is_file():
            raise ValueError(f"Video file does not exist: {value}")
        return value


class PlayerResponse(BaseModel):
    """Response model for player status"""

    status: player.PlayerStatus
    video_path: Optional[str] = None
    pid: Optional[int] = None
    uptime: Optional[float] = None
    error: Optional[str] = None


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "VLC Player Control API",
        "version": config.API_VERSION,
        "docs": "/docs",
    }


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api_version": config.API_VERSION}


@app.get("/player/status", response_model=PlayerResponse)
async def get_player_status():
    """
    Get the current status of the VLC player

    Returns:
        Player status information
    """
    try:
        status_value, status_info = player_manager.get_player_status()
        return {"status": status_value, **status_info}
    except Exception as e:
        logger.error("Error getting player status: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get player status: {str(e)}",
        ) from e


@app.post("/player/play", response_model=PlayerResponse)
async def play_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Start playing a video with VLC

    Args:
        request: Video request with path and options
        background_tasks: FastAPI background tasks

    Returns:
        Player status response
    """
    try:
        # Stop any existing playback
        if player_manager.vlc_process is not None:
            player_manager.stop_vlc_process()

        # Start new playback
        player_manager.vlc_process = player_manager.start_vlc_process(
            request.video_path, loop=request.loop, fullscreen=request.fullscreen
        )

        # Monitor the process in the background
        player_manager.monitor_vlc_process(background_tasks)

        # Get updated status
        status_value, status_info = player_manager.get_player_status()

        return {"status": status_value, **status_info}

    except FileNotFoundError as e:
        logger.error("Video file not found: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video file not found: {str(e)}",
        ) from e
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        ) from e


@app.post("/player/stop", response_model=PlayerResponse)
async def stop_video():
    """
    Stop the currently playing video

    Returns:
        Player status response
    """
    try:
        # Stop the playback
        player_manager.stop_vlc_process()

        # Get updated status
        status_value, status_info = player_manager.get_player_status()

        return {"status": status_value, **status_info}

    except Exception as e:
        logger.error("Error stopping video: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.post("/player/restart", response_model=PlayerResponse)
async def restart_video(background_tasks: BackgroundTasks):
    """
    Restart the currently playing video

    Returns:
        Player status response
    """
    try:
        # Check if a video is currently playing or was played
        if not player_manager.vlc_status["video_path"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No video has been played yet",
            )

        # Store the current video path
        video_path = player_manager.vlc_status["video_path"]

        # Stop the current playback
        player_manager.stop_vlc_process()

        # Start new playback with the same video
        player_manager.vlc_process = player_manager.start_vlc_process(video_path)

        # Monitor the process in the background
        player_manager.monitor_vlc_process(background_tasks)

        # Get updated status
        status_value, status_info = player_manager.get_player_status()

        return {"status": status_value, **status_info}

    except Exception as e:
        logger.error("Error restarting video: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.get("/secure-endpoint")
async def secure_endpoint(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "password":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "Secure access granted"}


@app.on_event("shutdown")
async def shutdown_event():
    if player_manager.vlc_process:
        player_manager.stop_vlc_process()
        logger.info("VLC process terminated during shutdown.")


if __name__ == "__main__":
    # Log startup information
    logger.info(
        "Starting VLC Player Control API on %s:%s", config.API_HOST, config.API_PORT
    )
    logger.info("Default VLC command: %s", " ".join(config.DEFAULT_VLC_COMMAND))

    # Run the server
    uvicorn.run(
        app=app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower(),
    )
