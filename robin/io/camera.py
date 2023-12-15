import cv2


class CameraCapture:
    def __init__(self, frame):
        self.frame = frame

    def save_to_file(self, path):
        cv2.imwrite(path, self.frame)


class Camera:
    def __init__(self, enabled=True, webcam_device_number=0):
        self.available = False
        if enabled:
            self.vc = cv2.VideoCapture(webcam_device_number)
            self.available = self.vc.isOpened()

    def get(self):
        if self.available:
            _, frame = self.vc.read()
            return CameraCapture(frame)
        return None
