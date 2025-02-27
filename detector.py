import cv2
import numpy as np
import time

class Detector:
    """
    Component responsible for detecting motion in frames received from the streamer
    and passing the detection information to the displayer.
    
    Uses frame differencing approach for motion detection as described in PyImageSearch tutorials.
    """
    def __init__(self, input_queue, output_queue):
        self.input_queue = input_queue
        self.output_queue = output_queue
        # Don't initialize OpenCV objects here as they can't be pickled
        # for Windows multiprocessing
        
    def start(self):
        print("Detector: Starting motion detection")
        
        # Initialize variables for frame differencing
        avg = None
        min_area = 500  # Minimum contour area to be considered motion
        
        # Give the camera sensor time to warmup
        time.sleep(0.1)
        
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
            
            # Resize the frame to reduce processing requirements (optional)
            # frame_copy = cv2.resize(frame_copy, (0, 0), fx=0.5, fy=0.5)
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise and improve accuracy
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # If this is the first frame, initialize the average
            if avg is None:
                print("Detector: Starting background model...")
                avg = gray.astype("float")
                continue
                
            # Accumulate the weighted average between the current frame and previous frames
            cv2.accumulateWeighted(gray, avg, 0.5)
            
            # Compute the absolute difference between the current frame and the running average
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
            
            # Threshold the delta image
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
            
            # Create a kernel for dilation
            kernel = np.ones((5,5), np.uint8)
            # Dilate the thresholded image to fill in holes
            thresh = cv2.dilate(thresh, kernel, iterations=2)
            
            # Find contours on the thresholded image
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Initialize the list of detections
            detections = []
            
            # Loop over the contours
            for contour in contours:
                # If the contour is too small, ignore it
                if cv2.contourArea(contour) < min_area:
                    continue
                    
                # Compute the bounding box for the contour
                x, y, w, h = cv2.boundingRect(contour)
                detections.append((x, y, w, h))
            
            # Send the original frame and detections to the displayer
            self.output_queue.put((frame, detections))
        
        print("Detector: Detection completed")