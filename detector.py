import cv2
import numpy as np

class Detector:
    """
    Component responsible for detecting motion in frames received from the streamer
    and passing the detection information to the displayer.
    """
    def __init__(self, input_queue, output_queue):
        self.input_queue = input_queue
        self.output_queue = output_queue
        # Don't initialize OpenCV objects here as they can't be pickled
        # for Windows multiprocessing
        
    def start(self):
        print("Detector: Starting motion detection")
        
        # Initialize the background subtractor here (after process has started)
        bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        
        while True:
            # Get a frame from the streamer
            frame = self.input_queue.get()
            
            # Check if it's the end of the video
            if frame is None:
                # Signal end of video to the displayer
                print("Detector: Received end-of-video signal")
                self.output_queue.put(None)
                break
            
            # Create a copy of the frame for detection processing
            # (original frame will be sent to displayer without modifications)
            frame_copy = frame.copy()
            
            # Apply background subtraction
            fg_mask = bg_subtractor.apply(frame_copy)
            
            # Threshold the mask to remove shadows (value 127)
            _, thresh = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours of moving objects
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours based on area to reduce noise
            detections = []
            for contour in contours:
                if cv2.contourArea(contour) > 100:  # Adjust threshold as needed
                    x, y, w, h = cv2.boundingRect(contour)
                    detections.append((x, y, w, h))
            
            # Send the original frame and detections to the displayer
            self.output_queue.put((frame, detections))
        
        print("Detector: Detection completed")