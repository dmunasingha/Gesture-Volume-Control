import subprocess
import time
from image_detection.utils import get_system_volume


class VolumeController:
    def __init__(self, smoothing_alpha=0.9, min_delta=0.5, update_interval=0.001):
        self.current_volume = get_system_volume()
        self.smoothing_alpha = smoothing_alpha
        self.min_delta = min_delta      # minimum change to trigger update
        self.last_update_time = 0
        self.update_interval = update_interval  # seconds

    def set_volume(self, target_volume):
        # Smooth with EMA
        smoothed = self.current_volume + self.smoothing_alpha * (target_volume - self.current_volume)

        # Clamp
        smoothed = max(0, min(100, smoothed))

        # Only update if significant change and enough time passed
        now = time.time()
        if abs(smoothed - self.current_volume) >= self.min_delta and (now - self.last_update_time) > self.update_interval:
            # Apply to macOS
            subprocess.run(["osascript", "-e", f"set volume output volume {int(smoothed)}"])
            self.last_update_time = now

        self.current_volume = smoothed
        return self.current_volume
