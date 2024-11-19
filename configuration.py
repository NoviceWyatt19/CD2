import os

# 기본 경로 설정
path_tpye = {
    'Mac': '/Users/wyatt/Desktop/CD2_project/',
    'Mac_cam': [0, 1, 2],
    'raspi': 'need to set',
    'raspi_cam': 'need to set',
}

# 데이터셋 사용자 설정
dataset_user = {
    'cam': 'cam_frame',
    'mctnn': 'detected_face_frame',
    'preprocessing': 'preprocessing_frame',
    'data_set': 'recog_user'
}

# 이미지 파일 형식
img_name = 'valid_frame_'
file_type = ['jpeg', 'jpg', 'png']

# 시리얼 포트 설정
ser_setting = {
    'Mac': '/dev/cu.usbmodemF412FA6F49D82',
    'voice1': '/dev/cu.usbmodem1301',
    'voice2': '/dev/cu.usbmodem11401',
    'voice3': '/dev/cu.usbmodem1401',
    'voice4': '/dev/cu.usbmodem11301',
    'test': '/dev/cu.usbmodem101',
    'Raspi': 'need to set',
    'Speed': [9600, 115200],
}

# 디렉터리 경로 설정
dir_path = {
    'Mac': {
        'cam': os.path.join(path_tpye['Mac'], dataset_user['cam']),  # cam_frame
        'mctnn': os.path.join(path_tpye['Mac'], dataset_user['mctnn']),  # detected_face_frame
        'preprocessing': os.path.join(path_tpye['Mac'], dataset_user['preprocessing']),  # preprocessing_frame
        'comp_db': os.path.join(path_tpye['Mac'], dataset_user['data_set'])  # recog_user
    },
    'Raspi': {}
}