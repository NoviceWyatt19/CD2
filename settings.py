path_tpye = {
    'Mac' : '/Users/wyatt/Desktop/CD2_project/',
    'raspi' : 'need to set',
}
dataset_user = {
    'cam' : 'cam_frame/',
    'mctnn' : 'detected_face_frame/',
    'embedding' : 'preprocessing_frame/',
}
# [
#     'cam_frame/',
#     'input raspi file path',
#     'detected_face_frame/',
# ]
img_name = 'valid_frame_'
file_type = ['jpeg', 'jpg', 'png']

save_cam_frame = {
    'Mac' : f'{path_tpye['Mac']}{dataset_user['cam']}',
    'Raspi' : f'need to set',
}
ser_setting = {
    'Mac' : '/dev/cu.usbmodemF412FA6F49D82',
    'Raspi' : f'need to set',
    'Speed' : [9600, 115200]
}