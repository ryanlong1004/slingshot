# VLC Player Control API

A simple Python API to control VLC media player for video playback through HTTP endpoints.

## Features

- Start/stop video playback
- Monitor playback status
- Control playback options (fullscreen, loop)
- Get health status and API information

## Requirements

- Python 3.7+
- VLC media player installed (cvlc command)
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```

## Running the API

Start the API server:

```bash
python vlc_api.py
```

This will start the API server on port 8000 (default).

## API Endpoints

- `GET /`: Root endpoint with basic information
- `GET /health`: Health check endpoint
- `GET /player/status`: Get current player status
- `POST /player/play`: Start playing a video
- `POST /player/stop`: Stop the current playback
- `POST /player/restart`: Restart the current video

## Usage Examples

### Play a video

```bash
curl -X POST http://localhost:8000/player/play \
  -H "Content-Type: application/json" \
  -d '{"video_path": "/path/to/your/video.mp4", "loop": true, "fullscreen": true}'
```

### Stop playback

```bash
curl -X POST http://localhost:8000/player/stop
```

### Get player status

```bash
curl http://localhost:8000/player/status
```

## Configuration

The VLC command can be modified by editing the `DEFAULT_VLC_COMMAND` variable in the `vlc_api.py` file.

## License

MIT

