import multiprocessing
import signal
import sys
import cv2
import argparse
import os
import threading
from streamer import Streamer
from detector import Detector
from displayer import Displayer

# Global references to processes for proper cleanup
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C and other termination signals."""
    print('\nSignal detected, shutting down all processes...')
    for process in processes:
        if process.is_alive():
            try:
                process.terminate()
                process.join(timeout=1.0)  # Wait for process to terminate with timeout
                if process.is_alive():
                    print(f"Process {process.name} didn't terminate cleanly, killing it")
                    if hasattr(process, 'kill'):
                        process.kill()
            except Exception as e:
                print(f"Error terminating process {process.name}: {e}")
    
    # Ensure OpenCV windows are closed
    cv2.destroyAllWindows()
    
    # Force exit without waiting for other threads
    os._exit(0)

def main(video_path):
    """
    Main function to set up and run the video analytics pipeline.
    
    Args:
        video_path: Path to the video file to process
    """
    global processes
    
    # Verify video path exists if it's a local file
    if not video_path.startswith(('http://', 'https://')) and not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return 1
    
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
    try:
        # Wait for processes while checking for interruptions
        while any(p.is_alive() for p in processes):
            for p in processes:
                if not p.is_alive():
                    print(f"Process {p.name} has terminated")
                    
                    # If the displayer terminated, terminate all other processes too
                    if p.name == "Displayer":
                        print("Displayer window closed, shutting down all processes...")
                        for other_p in processes:
                            if other_p.is_alive():
                                print(f"Terminating {other_p.name}...")
                                other_p.terminate()
                        break
            
            # Short sleep to prevent CPU spinning
            import time
            time.sleep(0.5)
            
            # Exit loop if all processes are terminated
            if not any(p.is_alive() for p in processes):
                break
                
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected!")
        # Handle the same way as the signal handler
        for process in processes:
            if process.is_alive():
                try:
                    process.terminate()
                    process.join(timeout=1.0)
                except Exception:
                    pass
        cv2.destroyAllWindows()
        os._exit(0)
    
    print("All processes have completed. System shutdown successful.")
    return 0

if __name__ == "__main__":
    # Set the multiprocessing start method explicitly (for Windows compatibility)
    multiprocessing.set_start_method('spawn', force=True)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Video Stream Analytics System')
    parser.add_argument('--video', type=str, required=True, 
                      help='Path to the video file or URL to process. Supports local files (.mp4, .avi, .mov, .mkv, etc.) and http/https URLs')
    args = parser.parse_args()
    
    # Run the main function
    sys.exit(main(args.video))