"""
Configuration settings for the VLC Player Control API.

This module contains configuration settings for:
- API server (host, port, etc.)
- VLC command and options
- Logging configuration
- Environment-specific settings

The configuration supports both development and production environments
through environment variables with sensible defaults.
"""

import logging
import os
import platform
from pathlib import Path
from typing import Dict, List, Union
from pydantic_settings import BaseSettings

# Fixed undefined BaseSettings issue and improved exception handling
try:
    from logging.handlers import RotatingFileHandler
except ImportError as exc:
    raise ImportError(
        "RotatingFileHandler is not available in the logging module"
    ) from exc

# ============================================================================
# Environment Detection
# ============================================================================
ENV = os.environ.get("API_ENV", "development").lower()
IS_PRODUCTION = ENV == "production"
IS_DEVELOPMENT = ENV == "development"
DEBUG = os.environ.get("DEBUG", "false").lower() == "true" or IS_DEVELOPMENT

# ============================================================================
# Paths Configuration
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = os.environ.get("LOG_DIR", str(BASE_DIR / "logs"))

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================================================
# VLC Command Configuration
# ============================================================================

# Detect operating system and set appropriate VLC path
if platform.system() == "Windows":
    DEFAULT_VLC_PATH = os.environ.get(
        "VLC_PATH", r"C:\Program Files\VideoLAN\VLC\vlc.exe"
    )
    # Use --dummy-quiet instead of --quiet on Windows
    QUIET_FLAG = "--dummy-quiet"
elif platform.system() == "Darwin":  # macOS
    DEFAULT_VLC_PATH = os.environ.get(
        "VLC_PATH", "/Applications/VLC.app/Contents/MacOS/VLC"
    )
    QUIET_FLAG = "--quiet"
else:  # Linux and others
    DEFAULT_VLC_PATH = os.environ.get("VLC_PATH", "/usr/bin/cvlc")
    QUIET_FLAG = "--quiet"

# Default video path (can be overridden by API clients)
DEFAULT_VIDEO_PATH = os.environ.get("DEFAULT_VIDEO_PATH", "/home/jinx/video.mp4")


# Build the VLC command based on platform
def get_vlc_command() -> List[str]:
    """
    Get the appropriate VLC command for the current platform

    Returns:
        List of command arguments
    """
    base_command = [DEFAULT_VLC_PATH]

    # For cvlc, we don't need to add --intf dummy since it's already a command-line interface
    if not DEFAULT_VLC_PATH.endswith("cvlc"):
        base_command.extend(["--intf", "dummy"])

    # Add other options
    base_command.extend(
        [
            "--no-osd",  # No on-screen display
            "--fullscreen",  # Start in fullscreen mode
            "--loop",  # Loop the video
            "--no-video-title-show",  # Don't show video title
            "--no-sub-autodetect-file",  # Don't auto-detect subtitle files
            QUIET_FLAG,  # Minimal console output
            "--drop-late-frames",  # Drop frames that arrive late
            "--skip-frames",  # Skip frames to maintain A/V sync
        ]
    )

    return base_command


# Default VLC command with all options
DEFAULT_VLC_COMMAND = get_vlc_command()

# ============================================================================
# API Configuration
# ============================================================================
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8000"))
API_VERSION = "1.0.0"
API_TITLE = "VLC Player Control API"
API_DESCRIPTION = "API for controlling VLC media player via HTTP endpoints"

# API CORS settings
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
CORS_METHODS = os.environ.get("CORS_METHODS", "GET,POST,OPTIONS").split(",")
CORS_HEADERS = os.environ.get("CORS_HEADERS", "*").split(",")

# Security settings
API_KEY_REQUIRED = os.environ.get("API_KEY_REQUIRED", "false").lower() == "true"
API_KEY = os.environ.get("API_KEY", "development_key")

# ============================================================================
# Logging Configuration
# ============================================================================
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE = os.path.join(LOG_DIR, os.environ.get("LOG_FILE", "vlc_api.log"))
LOG_MAX_SIZE = int(
    os.environ.get("LOG_MAX_SIZE", str(1024 * 1024 * 10))  # 10MB
)
LOG_BACKUP_COUNT = int(os.environ.get("LOG_BACKUP_COUNT", "3"))


# Configure logging
def setup_logging() -> logging.Logger:
    """
    Configure the application logging

    Returns:
        Logger: Configured logger instance
    """
    # Convert string log level to numeric value
    numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    # Create formatters and handlers
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)

    # Updated exception handling for file handler
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        handlers = [console_handler, file_handler]
    except Exception as e:
        print(
            "Warning: Could not create log file handler: {}. Using console only.".format(
                e
            )
        )
        handlers = [console_handler]

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=handlers,
    )

    # Create and return a custom logger
    logger = logging.getLogger("vlc-api")

    # Add environment info
    logger.info("Starting in %s mode", ENV)
    if DEBUG:
        logger.info("Debug mode is enabled")

    return logger


# ============================================================================
# Export application config as a dictionary for easy access
# ============================================================================
def get_config() -> Dict[str, Union[str, int, bool, List[str]]]:
    """
    Get all configuration as a dictionary

    Returns:
        Dict: All configuration values
    """
    return {
        "ENV": ENV,
        "DEBUG": DEBUG,
        "API_HOST": API_HOST,
        "API_PORT": API_PORT,
        "API_VERSION": API_VERSION,
        "API_TITLE": API_TITLE,
        "VLC_PATH": DEFAULT_VLC_PATH,
        "DEFAULT_VIDEO_PATH": DEFAULT_VIDEO_PATH,
        "LOG_LEVEL": LOG_LEVEL,
        "LOG_FILE": LOG_FILE,
    }


# Print configuration in debug mode
if DEBUG:
    print("=== VLC API Configuration ===")
    for key, value in get_config().items():
        print(f"{key}: {value}")
    print("=============================")


# ============================================================================
# Pydantic Settings Configuration
# ============================================================================
class Settings(BaseSettings):
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    LOG_LEVEL: str = "info"
    DEFAULT_VLC_COMMAND: str = "vlc"

    class Config:
        env_file = ".env"


settings = Settings()
