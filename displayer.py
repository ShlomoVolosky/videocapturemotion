import cv2
import datetime

class Displayer:
    """
    Component responsible for displaying frames, drawing detection boxes,
    adding timestamp, and applying blurring to detected regions.
    """
    def __init__(self, input_queue):
        self.input_queue = input_queue
        # Track motion status for text display
        self.motion_detected = False
        self.last_motion_time = None
        
    def blur_region(self, frame, x, y, w, h):
        """
        Apply Gaussian blur to a specific region in the frame.
        
        Args:
            frame: The image frame
            x, y, w, h: Region coordinates and dimensions
            
        Returns:
            Frame with the specified region blurred
        """
        # Make sure coordinates are within frame boundaries
        height, width = frame.shape[:2]
        x, y = max(0, x), max(0, y)
        w = min(w, width - x)
        h = min(h, height - y)
        
        # Extract the region of interest
        roi = frame[y:y+h, x:x+w]
        
        # Apply blurring to the region (Gaussian blur with 21x21 kernel)
        blurred_roi = cv2.GaussianBlur(roi, (25, 25), 0)
        
        # Place the blurred region back into the frame
        frame[y:y+h, x:x+w] = blurred_roi
        
        return frame
        
    def start(self):
        print("Displayer: Starting display")
        
        # Create window before entering the loop
        cv2.namedWindow('Video Analysis', cv2.WINDOW_NORMAL)
        
        # Initialize frame counter to wait for a few frames before checking window
        # This gives time for the window to actually appear
        frame_counter = 0
        
        while True:
            # Get frame and detections from the detector
            try:
                data = self.input_queue.get(timeout=1.0)  # Add timeout to check for window close periodically
            except Exception:
                # Check if window was closed, but only after we've displayed a few frames
                if frame_counter > 10 and cv2.getWindowProperty('Video Analysis', cv2.WND_PROP_VISIBLE) < 1:
                    print("Displayer: Window closed by user")
                    break
                continue
            
            # Check if it's the end of the video
            if data is None:
                print("Displayer: Received end-of-video signal")
                break
            
            frame, detections = data
            
            # Update motion status
            if len(detections) > 0:
                self.motion_detected = True
                self.last_motion_time = datetime.datetime.now()
            elif self.last_motion_time is not None:
                # Reset motion flag after 2 seconds of no motion
                time_difference = (datetime.datetime.now() - self.last_motion_time).total_seconds()
                if time_difference > 2.0:
                    self.motion_detected = False
            
            # Draw detections and apply blurring on the frame
            for x, y, w, h in detections:
                # First blur the detection region
                frame = self.blur_region(frame, x, y, w, h)
                
                # Then draw the rectangle around the blurred region
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Add text label above the detection
                label = "Motion"
                cv2.putText(frame, label, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Add current time to the frame (upper left corner)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, current_time, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 
                      0.5, (0, 0, 255), 2, cv2.LINE_AA)
            
            # Add motion status text
            status_text = "Status: {}".format("Motion Detected" if self.motion_detected else "No Motion")
            status_color = (0, 0, 255) if self.motion_detected else (0, 255, 0)
            cv2.putText(frame, status_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                      0.5, status_color, 2, cv2.LINE_AA)
            
            # Display the frame
            cv2.imshow('Video Analysis', frame)
            
            # Increment frame counter
            frame_counter += 1
            
            # Check for key press (q to quit)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Displayer: Quit key pressed")
                break
            
            # Check if window was closed, but only after we've displayed a few frames
            if frame_counter > 10 and cv2.getWindowProperty('Video Analysis', cv2.WND_PROP_VISIBLE) < 1:
                print("Displayer: Window closed by user")
                break
        
        # Clean up
        cv2.destroyAllWindows()
        print("Displayer: Display completed")