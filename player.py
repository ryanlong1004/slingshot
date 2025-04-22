"""
VLC Player process management module.

This module handles the creation, monitoring, and termination of VLC processes
for video playback.
"""

import os
import subprocess
import time
import signal  # Add missing import for signal module
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from fastapi import BackgroundTasks

import config

# Configure logger
logger = config.setup_logging()


class PlayerStatus(str, Enum):
    """Enum representing possible player statuses"""

    PLAYING = "playing"
    STOPPED = "stopped"
    ERROR = "error"


class VLCPlayerManager:
    def __init__(self):
        self.vlc_process: Optional[subprocess.Popen] = None
        self.vlc_status: Dict[str, Any] = {
            "running": False,
            "video_path": None,
            "start_time": None,
            "pid": None,
            "error": None,
        }

    def build_vlc_command(
        self, video_path: str, loop: bool = True, fullscreen: bool = True
    ) -> List[str]:
        """
        Build the VLC command with the specified options.

        Args:
            video_path: Path to the video file
            loop: Whether to loop the video
            fullscreen: Whether to play in fullscreen mode

        Returns:
            List of command arguments
        """
        cmd = config.DEFAULT_VLC_COMMAND.copy()

        # Modify options based on parameters
        if not loop:
            cmd = [arg for arg in cmd if arg != "--loop"]

        if not fullscreen:
            cmd = [arg for arg in cmd if arg != "--fullscreen"]

        # Add the video path
        cmd.append(video_path)

        logger.debug("Built VLC command: %s", " ".join(cmd))
        return cmd

    def start_vlc_process(
        self, video_path: str, loop: bool = True, fullscreen: bool = True
    ) -> None:
        """
        Start the VLC process.

        Args:
            video_path: Path to the video file
            loop: Whether to loop the video
            fullscreen: Whether to play in fullscreen mode
        """
        if not os.path.exists(video_path):
            error_msg = f"Video file not found: {video_path}"
            logger.error(error_msg)
            self.vlc_status["error"] = error_msg
            raise FileNotFoundError(error_msg)

        try:
            cmd = self.build_vlc_command(video_path, loop, fullscreen)
            logger.info("Starting VLC with command: %s", " ".join(cmd))

            # Start the VLC process with appropriate settings for platform
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )

            # Update status
            self.vlc_process = process
            self.vlc_status.update(
                {
                    "running": True,
                    "video_path": video_path,
                    "start_time": time.time(),
                    "pid": process.pid,
                    "error": None,
                }
            )

            logger.info("VLC process started with PID %d", process.pid)

        except FileNotFoundError as exc:
            error_msg = f"Video file not found: {video_path}"
            logger.error(error_msg)
            self.vlc_status["error"] = error_msg
            raise FileNotFoundError(error_msg) from exc
        except subprocess.SubprocessError as e:  # More specific exception
            error_msg = f"Failed to start VLC process: {str(e)}"
            logger.error(error_msg)
            self.vlc_status["error"] = error_msg
            self.vlc_status["running"] = False
            raise RuntimeError(error_msg) from e

    def stop_vlc_process(self) -> bool:
        """
        Stop the VLC process.

        Returns:
            True if process was stopped, False otherwise
        """
        if self.vlc_process is None:
            logger.info("No VLC process to stop")
            return False

        logger.info("Stopping VLC process with PID %d", self.vlc_process.pid)

        try:
            if self.vlc_process.poll() is None:
                self.vlc_process.terminate()
                try:
                    self.vlc_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("VLC process did not terminate, killing forcefully")
                    os.killpg(os.getpgid(self.vlc_process.pid), signal.SIGKILL)

            # Update status
            self.vlc_status.update(
                {"running": False, "video_path": None, "start_time": None}
            )

            logger.info("VLC process stopped")
            return True

        except Exception as e:
            error_msg = f"Error stopping VLC process: {str(e)}"
            logger.error(error_msg)
            self.vlc_status["error"] = error_msg
            return False
        finally:
            self.vlc_process = None

    def get_player_status(self) -> Tuple[PlayerStatus, Dict[str, Any]]:
        """
        Get the current status of the player.

        Returns:
            Tuple containing PlayerStatus and dictionary with detailed status info
        """
        uptime = None
        if self.vlc_status["start_time"] is not None:
            uptime = time.time() - self.vlc_status["start_time"]

        if self.vlc_status["running"] and self.vlc_process:
            if self.vlc_process.poll() is not None:
                self.vlc_status["running"] = False
                self.vlc_status["error"] = (
                    f"VLC process exited with code {self.vlc_process.returncode}"
                )
                player_status = PlayerStatus.ERROR
            else:
                player_status = PlayerStatus.PLAYING
        elif self.vlc_status["running"]:
            self.vlc_status["running"] = False
            self.vlc_status["error"] = "VLC process reference lost"
            player_status = PlayerStatus.ERROR
        elif self.vlc_status["error"]:
            player_status = PlayerStatus.ERROR
        else:
            player_status = PlayerStatus.STOPPED

        status_info = {
            "video_path": self.vlc_status["video_path"],
            "pid": self.vlc_status["pid"],
            "uptime": uptime,
            "error": self.vlc_status["error"],
        }

        return player_status, status_info

    def monitor_vlc_process(self, background_tasks: BackgroundTasks) -> None:
        """
        Monitor the VLC process in the background.

        Args:
            background_tasks: FastAPI background tasks
        """
        if self.vlc_process is None:
            return

        def _monitor():
            pid = self.vlc_process.pid if self.vlc_process else None
            logger.info("Starting to monitor VLC process with PID %d", pid)

            try:
                if self.vlc_process and self.vlc_process.poll() is None:
                    exit_code = self.vlc_process.wait()
                    logger.info("VLC process exited with code %d", exit_code)

                    if exit_code != 0:
                        errors = (
                            self.vlc_process.stderr.read()
                            if self.vlc_process.stderr
                            else "Unknown error"
                        )
                        self.vlc_status["error"] = (
                            "VLC process exited with code %d: %s" % (exit_code, errors)
                        )

                    self.vlc_status.update(
                        {
                            "running": False,
                            "pid": None,
                        }
                    )
                    self.vlc_process = None

            except Exception as e:
                logger.error("Error monitoring VLC process: %s", str(e))
                self.vlc_status["error"] = str(e)
                self.vlc_status["running"] = False
                self.vlc_process = None

        background_tasks.add_task(_monitor)

    def cleanup_on_exit(self):
        """
        Clean up VLC process on application exit.
        """
        if self.vlc_process is not None:
            logger.info("Application shutting down. Stopping VLC process...")
            self.stop_vlc_process()


# Register cleanup function to be called on application exit
player_manager = VLCPlayerManager()
