"""
Animation effects for the Fortune Teller command-line application.
"""
import time
import sys
import threading
from typing import Optional

from fortune_teller.ui.colors import Colors

class LoadingAnimation:
    """Class to handle loading animation in the console."""
    
    def __init__(self, message: str = "处理中"):
        """
        Initialize the loading animation.
        
        Args:
            message: Message to display with the animation
        """
        self.message = message
        self.stop_event = threading.Event()
        self.loading_thread = None
        self.chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        self.start_time = 0
    
    def _animation_loop(self):
        """Animation loop to be run in a thread."""
        i = 0
        while not self.stop_event.is_set():
            elapsed = int(time.time() - self.start_time)
            sys.stdout.write(f"\r{Colors.YELLOW}{self.chars[i % len(self.chars)]}{Colors.ENDC} {self.message} ({elapsed}秒)...")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
            if elapsed > 60:  # After 1 minute, show a different message
                sys.stdout.write(f"\r{Colors.YELLOW}⏳{Colors.ENDC} {self.message}，请耐心等待 ({elapsed}秒)...")
                sys.stdout.flush()
    
    def start(self) -> None:
        """Start the animation in a background thread."""
        self.stop_event.clear()
        self.start_time = time.time()
        self.loading_thread = threading.Thread(target=self._animation_loop)
        self.loading_thread.daemon = True
        self.loading_thread.start()
    
    def stop(self) -> None:
        """Stop the animation and clean up."""
        if self.loading_thread and self.loading_thread.is_alive():
            self.stop_event.set()
            self.loading_thread.join(0.5)  # Wait up to 0.5 seconds for thread to terminate
            
            # Clear the animation line
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()
