import cv2

class Camera:

    """camera_index defaulted to 0 (if you have 1 camera, this will be its index),
        if you have multiple, you can choose to use a different camera
    """ 
    def __init__(self, camera_index=0):                
        self.cap = cv2.VideoCapture(camera_index)       #openCV opens connection to webcam
        if not self.cap.isOpened():
            raise RuntimeError("ERROR: Webcam connection failed! Check that it is connected and/or not in use.")

    def read_frame(self):
        """Read a single frame from the webcam. Returns (success boolean, frame object)."""
        ret, frame = self.cap.read()
        if not ret:
            return False, None
        frame = cv2.flip(frame, 1)  #mirror the frame so you don't get self-conscious about how you look
        return True, frame

    def release(self):
        """Release the webcam and close any OpenCV windows."""
        self.cap.release()
        cv2.destroyAllWindows()
