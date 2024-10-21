import face_detection as ff
import video_frame_filter as vff
import time

cnt = 1
vff.max_frame = 300

def get_frame(capture):
    ret, frame = capture.read()
    if not ret:
        raise Exception("Failed to grab frame")
    return frame

# take a picture
try:
    vff.main()
    while cnt <= vff.max_frame:
        ff.detect_N_mark_face(cnt) # d_type : img, webcam
        cnt += 1

finally:
    time.sleep(2)

# frame preprocessing
