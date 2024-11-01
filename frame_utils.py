import cv2

def get_frame(capture):
    ret, frame = capture.read()
    if not ret:
        raise Exception("Failed to grab frame")
    return frame