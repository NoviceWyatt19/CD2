import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import face_detection as ff
import video_frame_filter as vff
import time
from frame_utils import get_frame

cnt = 1
vff.max_frame = 300

# take a picture
try:
    vff.main()
    while cnt <= vff.max_frame:
        ff.detect_N_mark_face(cnt) # d_type : img, webcam
        cnt += 1

finally:
    time.sleep(2)

# frame preprocessing
