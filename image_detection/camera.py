import cv2

class Camera:
    def __init__(self, device=0):
        self.cap = cv2.VideoCapture(device)

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

class CameraError(Exception):
    pass