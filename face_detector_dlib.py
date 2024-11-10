import dlib
import cv2

# dlib 초기화
detector_dlib = dlib.get_frontal_face_detector()

def process_image_dlib(image):
    gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector_dlib(gray_frame)
    
    for face in faces:
        x, y, x1, y1 = face.left(), face.top(), face.right(), face.bottom()
        cv2.rectangle(image, (x, y), (x1, y1), (0, 255, 0), 2)
    
    return image, faces