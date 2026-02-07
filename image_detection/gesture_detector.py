import math
import numpy as np
from image_detection.utils import get_system_volume


class GestureDetector:
    def __init__(self):
        self.start_vector = None       # Vector at gesture start
        self.prev_angle = None         # Previous angle
        self.current_volume = get_system_volume()       # Initial volume
        self.ANGLE_THRESHOLD = 2       # Minimum degrees to register change
        self.VOLUME_RANGE = 20        # Degrees for full 0-100% volume
        self.SMOOTHING_ALPHA = 0.2     # EMA smoothing
        self.last_update_time = 0


    def detect(self, landmarks):
        if not landmarks:
            # no hands
            self.reset()
            return None, self.current_volume

        # --- Check for "both hands up" gesture ---
        if len(landmarks) >= 2:
            hand1 = landmarks[0]
            hand2 = landmarks[1]

            def hand_up_and_fingers_extended(hand):
                wrist = np.array(hand[0])
                fingers = [4, 8, 12, 16, 20]  # Thumb to pinky tips
                for i in fingers:
                    tip = np.array(hand[i])
                    # Finger must be above wrist and sufficiently extended
                    if tip[1] > wrist[1] or np.linalg.norm(tip - wrist) < 0.05:
                        return False
                return True

            if hand_up_and_fingers_extended(hand1) and hand_up_and_fingers_extended(hand2):
                self.reset()
                return "BOTH_HANDS_UP", self.current_volume


        hand = landmarks[0]

        # --- Index finger rotation ---
        wrist = np.array(hand[0])
        thumb_tip = np.array(hand[4])
        index_tip = np.array(hand[8])
        pinch_dist = np.linalg.norm(thumb_tip - index_tip)

        if pinch_dist < 0.08:  # Start gesture when thumb and index are close
            current_vector = index_tip - wrist
            norm = np.linalg.norm(current_vector)
            if norm < 1e-6:
                return None, self.current_volume
            current_vector /= norm

            # --- Initialize start vector ---
            if self.start_vector is None:
                self.start_vector = current_vector
                self.prev_angle = 0
                return "GESTURE_START", self.current_volume

            # --- Compute angle in XY plane ---
            v1 = self.start_vector[:2]
            v2 = current_vector[:2]
            dot = np.dot(v1, v2)
            cross = np.cross(v1, v2)
            angle_rad = np.arctan2(cross, dot)
            angle_deg = math.degrees(angle_rad)

            # --- Delta rotation ---
            delta_angle = angle_deg - self.prev_angle
            # map to -180..180
            if delta_angle > 180:
                delta_angle -= 360
            elif delta_angle < -180:
                delta_angle += 360

            # --- Apply threshold ---
            if abs(delta_angle) < self.ANGLE_THRESHOLD:
                return "ROTATE", self.current_volume

            # --- Map rotation to volume ---
            volume_change = (delta_angle / self.VOLUME_RANGE) * 100
            target_volume = self.current_volume + volume_change
            target_volume = max(0, min(100, target_volume))

            # --- Smooth volume ---
            smoothed_volume = self.current_volume + self.SMOOTHING_ALPHA * (target_volume - self.current_volume)
            self.current_volume = smoothed_volume

            # --- Update system volume ---
            self.prev_angle = angle_deg

            return f"ROTATE_{angle_deg:.1f}°", self.current_volume
        else:
            self.reset()
            return None, self.current_volume

    def reset(self):
        """Call when hand is removed or gesture ends"""
        self.start_vector = None
        self.prev_angle = None
