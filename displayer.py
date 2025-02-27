import cv2
import datetime

class Displayer:
    """
    Component responsible for displaying frames, drawing detection boxes,
    adding timestamp, and applying blurring to detected regions.
    """
    def __init__(self, input_queue):
        self.input_queue = input_queue
        
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
        blurred_roi = cv2.GaussianBlur(roi, (21, 21), 0)
        
        # Place the blurred region back into the frame
        frame[y:y+h, x:x+w] = blurred_roi
        
        return frame
        
    def start(self):
        print("Displayer: Starting display")
        
        while True:
            # Get frame and detections from the detector
            data = self.input_queue.get()
            
            # Check if it's the end of the video
            if data is None:
                print("Displayer: Received end-of-video signal")
                break
            
            frame, detections = data
            
            # Draw detections and apply blurring on the frame
            for x, y, w, h in detections:
                # First blur the detection region
                frame = self.blur_region(frame, x, y, w, h)
                
                # Then draw the rectangle around the blurred region
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Add current time to the frame (upper left corner)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                      0.8, (0, 0, 255), 2, cv2.LINE_AA)
            
            # Display the frame
            cv2.imshow('Video Analysis', frame)
            
            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Clean up
        cv2.destroyAllWindows()
        print("Displayer: Display completed")