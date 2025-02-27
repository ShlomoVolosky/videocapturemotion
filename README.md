# Video Stream Analytics System

A Python-based pipeline system for video processing with motion detection and blurring capabilities. The system processes video streams from various sources, detects motion, and applies blurring to detected regions.

## Features

- Pipeline architecture with three independent components running as separate processes
- Support for multiple video sources (local files, URLs, webcam)
- Motion detection using frame differencing approach
- Automatic blurring of detected motion regions
- Real-time timestamp and motion status display
- Multiple video format support (.mp4, .avi, .mov, .mkv, etc.)
- Proper system shutdown when video ends

## Installation

### Requirements

- Python 3.6+
- OpenCV
- NumPy

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ShlomoVolosky/videocapturemotion.git
cd video_capture
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. Install the dependencies:
```bash
pip install -r requirements.txt
```

## How to Test the Code

The system can process video from different sources. Here are the specific commands to test various video sources:

### 1. Testing with a Local Video File

```bash
python main.py --video path/to/your/video.avi
```

### 2. Testing with Your Webcam

To use your webcam as the video source, can run:

```bash
python -c "import cv2; cap = cv2.VideoCapture(0); fourcc = cv2.VideoWriter_fourcc(*'XVID'); out = cv2.VideoWriter('test_video.avi', fourcc, 20.0, (640, 480)); [out.write(frame) for ret, frame in [cap.read() for _ in range(200)] if ret]; cap.release(); out.release()"
```

```bash
python main.py --video 0
```

Note: The `0` refers to the first webcam device. Use `1`, `2`, etc. for additional webcams if available.

### 3. Testing with the Big Buck Bunny Sample Video URL

```bash
python main.py --video https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
```

## System Architecture

The system consists of three main components:

1. **Streamer**: Reads frames from the video source and sends them to the Detector
2. **Detector**: Analyzes frames to detect motion and forwards detection data to the Displayer
3. **Displayer**: Applies blurring to detected regions and displays the processed video

Each component runs as a separate process, communicating through multiprocessing queues.

## Controls

While the video is playing:
- Press `q` to quit at any time
- Close the video window to exit the application

## Troubleshooting

- **Video Not Found Error**: Ensure the file path is correct for local videos
- **No Motion Detection**: Try adjusting lighting conditions or increasing movement in the frame
- **Window Closes Immediately**: Ensure OpenCV is properly installed and can access your display
- **Process Termination Issues**: If Ctrl+C doesn't terminate properly, close the video window instead

## Example Output

When running properly, you should see:
- A window showing the video stream
- Green rectangles highlighting areas with detected motion
- Those same areas being blurred for privacy
- A timestamp in the upper left corner
- A status message showing "Motion Detected" or "No Motion"
