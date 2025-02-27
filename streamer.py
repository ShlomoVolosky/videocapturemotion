import cv2
import time
import re
import urllib.request
import os

class Streamer:
    """
    Component responsible for reading frames from a video and sending them to the detector.
    Supports both local file paths and HTTP/HTTPS URLs, with multiple video formats.
    """
    def __init__(self, video_path, output_queue):
        self.video_path = video_path
        self.output_queue = output_queue
        # Common supported video formats by OpenCV
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.mpg', '.mpeg']
        
    def is_url(self, path):
        """Check if the provided path is a URL"""
        url_pattern = re.compile(r'^https?://.*$')
        return bool(url_pattern.match(path))
    
    def get_file_extension(self, path):
        """Get the file extension from a path"""
        if self.is_url(path):
            # For URLs, extract extension from the path portion
            file_path = path.split('?')[0]  # Remove query parameters
            return os.path.splitext(file_path)[1].lower()
        else:
            # For local files
            return os.path.splitext(path)[1].lower()
        
    def start(self):
        # Check file extension if it's not a URL
        if not self.is_url(self.video_path):
            extension = self.get_file_extension(self.video_path)
            if extension and extension not in self.supported_formats:
                print(f"Warning: File extension '{extension}' might not be supported. Attempting to open anyway.")
                print(f"Supported formats include: {', '.join(self.supported_formats)}")
        
        # Print source type for debugging
        source_type = "URL" if self.is_url(self.video_path) else "local file"
        print(f"Streamer: Opening video from {source_type}: {self.video_path}")
        
        # Check connectivity if it's a URL
        if self.is_url(self.video_path):
            try:
                # Try to connect to the URL to verify it's accessible
                request = urllib.request.Request(
                    self.video_path, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                urllib.request.urlopen(request, timeout=5)
                print("Streamer: URL is accessible")
            except Exception as e:
                print(f"Streamer: Error accessing URL: {e}")
                print("Streamer: Will still attempt to open with OpenCV...")
        
        # Open the video file or URL
        video = cv2.VideoCapture(self.video_path)
        
        # Check if video opened successfully
        if not video.isOpened():
            print(f"Error: Could not open video from {source_type}.")
            return
        
        # Get video properties for proper playback timing
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_delay = 1 / fps if fps > 0 else 1/30  # Default to 30 FPS if unable to determine
        
        print(f"Streamer: Starting video stream at {fps} FPS")
        
        # Process the video frame by frame
        while True:
            # Read a frame
            ret, frame = video.read()
            
            # If frame is read correctly ret is True
            if not ret:
                # End of video
                print("Streamer: End of video reached")
                self.output_queue.put(None)  # Signal end of video
                break
            
            # Send the frame to the detector
            self.output_queue.put(frame)
            
            # Control the frame rate to match the original video
            time.sleep(frame_delay)
        
        # Release the video
        video.release()
        print("Streamer: Video processing completed")