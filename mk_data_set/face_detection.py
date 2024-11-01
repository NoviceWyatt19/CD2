from mtcnn.mtcnn import MTCNN
import configuration as con
import cv2
import os
import numpy as np
from mk_data_set.user_face_data_collector import get_frame

def resize_N_pad(img, size=(160, 160)):
    h, w, _ = img.shape
    target_h, target_w = size

    # Scaling
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Padding
    delta_w = target_w - new_w
    delta_h = target_h - new_h
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)
    color = [0, 0, 0]  # Black padding

    new_img = cv2.copyMakeBorder(resized_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return new_img

def detect_N_mark_face(frame, cnt, d_type='img'):
    detector = MTCNN()

    if d_type == 'img':
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = detector.detect_faces(img_rgb)
        detected = len(result) > 0

        if detected:
            for person in result:  # Mark on the frame
                bounding_box = person['box']
                x, y, width, height = bounding_box
                face = img_rgb[y:y + height, x:x + width]  # Crop face
                face_160x160 = resize_N_pad(face)  # Resize and pad to 160x160

                # Save the cropped face
                output_path = f'{con.dir_path["Mac"]["mctnn"]}cropped_face_{cnt}.png'
                cv2.imwrite(output_path, cv2.cvtColor(face_160x160, cv2.COLOR_RGB2BGR))
                print(f"Cropped face saved at {output_path}")
        else:
            print("No face detected.")
    
    elif d_type == 'webcam':  # Webcam face detection and drawing rects
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = detector.detect_faces(img_rgb)

        if result:
            for person in result:
                bounding_box = person['box']
                x, y, width, height = bounding_box
                cv2.rectangle(frame,
                              (x, y),
                              (x + width, y + height),
                              (0, 255, 0), 2)
        return frame

if __name__ == "__main__":
    try:
        cnt = 1
        # Example of receiving frames from a shared source
        while cnt <= 200:
            # Assume `get_frame()` is a function that returns the current frame from VideoCapture
            frame = get_frame()  # This function would be defined in another part of the code
            detect_N_mark_face(frame, cnt, d_type='img')  # For image mode
            cnt += 1
    except Exception as e:
        print(f"An error occurred: {e}")