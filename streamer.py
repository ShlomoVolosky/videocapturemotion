import cv2
import time

class Streamer:
    """
    Component responsible for reading frames from a video and sending them to the detector.
    """
    def __init__(self, video_path, output_queue):
        self.video_path = video_path
        self.output_queue = output_queue
        
    def start(self):
        # Open the video file
        video = cv2.VideoCapture(self.video_path)
        
        # Check if video opened successfully
        if not video.isOpened():
            print("Error: Could not open video.")
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