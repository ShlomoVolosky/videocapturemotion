import multiprocessing
import signal
import sys
import cv2
import argparse
from streamer import Streamer
from detector import Detector
from displayer import Displayer

# Global references to processes for proper cleanup
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C and other termination signals."""
    print('Signal detected, shutting down all processes...')
    for process in processes:
        if process.is_alive():
            process.terminate()
    cv2.destroyAllWindows()
    sys.exit(0)

def main(video_path):
    """
    Main function to set up and run the video analytics pipeline.
    
    Args:
        video_path: Path to the video file to process
    """
    global processes
    
    # Set up signal handler for proper cleanup on Ctrl+C and other signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create the queues for inter-process communication
    streamer_to_detector = multiprocessing.Queue(maxsize=5)  # Limit queue size to prevent memory issues
    detector_to_displayer = multiprocessing.Queue(maxsize=5)
    
    # Create the component instances
    streamer = Streamer(video_path, streamer_to_detector)
    detector = Detector(streamer_to_detector, detector_to_displayer)
    displayer = Displayer(detector_to_displayer)
    
    # Create processes
    streamer_process = multiprocessing.Process(target=streamer.start, name="Streamer")
    detector_process = multiprocessing.Process(target=detector.start, name="Detector")
    displayer_process = multiprocessing.Process(target=displayer.start, name="Displayer")
    
    processes = [streamer_process, detector_process, displayer_process]
    
    # Start the processes
    print(f"Starting video analysis pipeline for: {video_path}")
    for process in processes:
        process.start()
        print(f"Started {process.name} process (PID: {process.pid})")
    
    # Wait for processes to complete
    for process in processes:
        process.join()
    
    print("All processes have completed. System shutdown successful.")

if __name__ == "__main__":
    # Set the multiprocessing start method
    if sys.platform == 'win32':
        multiprocessing.set_start_method('spawn')
    else:
        multiprocessing.set_start_method('fork')
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Video Stream Analytics System')
    parser.add_argument('--video', type=str, required=True, 
                      help='Path to the video file or URL to process. Supports local files (.mp4, .avi, .mov, .mkv, etc.) and http/https URLs')
    args = parser.parse_args()
    
    # Run the main function
    main(args.video)