# Video Stream Analytics System

This project implements a video analytics system with motion detection and blurring capabilities. The system processes video streams, detects motion, and applies blurring to the detected regions while displaying the result.

## Architecture

The system follows a pipeline architecture with three main components:

1. **Streamer**: Reads frames from a video source and forwards them to the Detector
2. **Detector**: Analyzes frames to identify motion and forwards frames with detection metadata to the Displayer
3. **Displayer**: Displays frames with detection boxes, applies blurring to detected regions, and adds timestamps

Each component runs as a separate process, communicating through queues.

## Implementation Details

### Communication Method

The system uses `multiprocessing.Queue` for inter-process communication because:
- It's specifically designed for sharing data between Python processes
- It's thread-safe and process-safe
- It can handle arbitrary Python objects (frames and detection data)
- It's part of the standard library, making the solution portable
- It provides built-in synchronization and buffering

### Motion Detection

Motion detection is implemented using OpenCV's `BackgroundSubtractorMOG2`. This background subtraction algorithm creates a foreground mask by taking a frame and subtracting it from the background model, identifying moving objects.

### Blurring Algorithm

The system uses Gaussian blur (via `cv2.GaussianBlur`) to obfuscate detected regions. This provides an efficient way to blur movement areas while maintaining the overall frame integrity.

### Shutdown Mechanism

The system implements proper shutdown when a video ends through a signaling system:
1. When the Streamer reaches the end of the video, it sends a `None` value to the Detector
2. The Detector forwards this signal to the Displayer
3. Each component terminates upon receiving this signal
4. The main process waits for all components to finish using `join()`

Additionally, signal handlers are set up to handle external termination requests (Ctrl+C).

## Running the System

To run the system, use the following command:

### With a local video file (multiple formats supported):
```bash
python main.py --video path/to/video.mp4
python main.py --video path/to/video.avi
python main.py --video path/to/video.mov
python main.py --video path/to/video.mpg
```

### With a video from a URL:
```bash
python main.py --video https://example.com/path/to/video.mp4
```

The system supports both local video files and HTTP/HTTPS URLs as video sources. OpenCV can handle numerous video formats including MP4, AVI, MOV, MPG, MPEG, MKV, WMV, and more.

## Requirements

- Python 3.6+
- OpenCV (`pip install opencv-python`)

## Step Implementation

The code is organized to clearly separate the three implementation steps:

1. Building a system that performs analytics on video streams (all files)
2. Adding a Blurring component (implemented in `displayer.py`)
3. Shutting down the system when a video ends (implemented in all files with proper signal handling)