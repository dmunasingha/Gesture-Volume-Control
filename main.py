import cv2
from image_detection.camera import Camera
from image_detection.hand_tracker import HandTracker
from image_detection.gesture_detector import GestureDetector
from image_detection.volume_controller import VolumeController

def main():
    tracker = HandTracker()
    gestures = GestureDetector()
    volume_ctrl = VolumeController()

    with Camera() as cam:
        while True:
            frame = cam.read()
            if frame is None:
                continue

            frame, landmarks = tracker.process(frame)

            gesture, target_volume = gestures.detect(landmarks)

            if gesture:
                # Smoothly apply volume
                current_volume = volume_ctrl.set_volume(target_volume)

                # Display gesture and volume
                cv2.putText(
                    frame,
                    f"{gesture} | Volume: {int(current_volume)}%",
                    (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (255, 0, 0),
                    3
                )

                if gesture == "BOTH_HANDS_UP":  # Close the program on both hands up
                    print("Both hands up detected. Exiting...")
                    break

            cv2.imshow("Hand Tracking & Gestures", frame)

            key = cv2.waitKey(1)
            if key in [27, ord('q')]:
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
