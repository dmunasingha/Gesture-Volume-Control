# hand_tracker.py
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time


# Standard 21 hand landmarks connections (same as old HAND_CONNECTIONS)
HAND_CONNECTIONS = frozenset([
    (0, 1), (1, 2), (2, 3), (3, 4),      # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),      # index
    (0, 9), (9, 10), (10, 11), (11, 12), # middle
    (0, 13), (13, 14), (14, 15), (15, 16), # ring
    (0, 17), (17, 18), (18, 19), (19, 20), # pinky
    (5, 9), (9, 13), (13, 17)            # between fingers
])


class HandTracker:
    def __init__(self,
                 model_path="models/hand_landmarker.task",  # place this file in your project folder
                 max_num_hands=2,
                 min_detection_conf=0.5,
                 min_tracking_conf=0.5):

        base_options = python.BaseOptions(
            model_asset_path=model_path,
            delegate=python.BaseOptions.Delegate.CPU  # GPU possible on Mac with extra setup
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_conf,
            min_tracking_confidence=min_tracking_conf
        )

        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def process(self, frame):
        if frame is None:
            return frame, []
        
        # BGR → RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = int(time.time() * 1000)

        results = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        landmarks = []  # list of lists: [ hand1_points, hand2_points, ... ]

        if results.hand_landmarks:
            h, w = frame.shape[:2]

            for hand_lmks in results.hand_landmarks:
                # Collect normalized (x,y,z)
                points = [(lm.x, lm.y, lm.z) for lm in hand_lmks]
                landmarks.append(points)

                # Draw circles on landmarks
                for lm in hand_lmks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), radius=6, color=(0, 255, 0), thickness=-1)

                # Draw connections
                for conn in HAND_CONNECTIONS:
                    i1, i2 = conn
                    if i1 < len(hand_lmks) and i2 < len(hand_lmks):
                        p1 = hand_lmks[i1]
                        p2 = hand_lmks[i2]
                        x1, y1 = int(p1.x * w), int(p1.y * h)
                        x2, y2 = int(p2.x * w), int(p2.y * h)
                        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)

            # Optional: show Left/Right
            if results.handedness:
                for handedness, hand_lmks in zip(results.handedness, results.hand_landmarks):
                    label = handedness[0].category_name  # 'Left' or 'Right'
                    # Place text near wrist (landmark 0)
                    wrist = hand_lmks[0]
                    tx = int(wrist.x * w) - 60
                    ty = int(wrist.y * h) - 40
                    cv2.putText(frame, label, (tx, ty),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        return frame, landmarks