import time


class FPSTracker:
    def __init__(self):
        self.frame_count = 0
        self.start_time = time.time()

    def update(self):
        """Update frame count and calculate FPS if more than 1 second has passed."""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time

        if elapsed_time > 1.0:
            fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
            return fps
        return 0
