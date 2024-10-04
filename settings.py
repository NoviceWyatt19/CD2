path_tpye = {
    'Mac' : '/Users/wyatt/Desktop/CD2_project/',
    'Mac_cam' : [0, 1, 2],
    'raspi' : 'need to set',
    'raspi_cam' : 'need to set',
}
dataset_user = {
    'cam' : 'cam_frame/',
    'mctnn' : 'detected_face_frame/',
    'embedding' : 'preprocessing_frame/',
    'data_set' : 'recog_user/'
}
img_name = 'valid_frame_'

file_type = ['jpeg', 'jpg', 'png']

ser_setting = {
    'Mac' : '/dev/cu.usbmodemF412FA6F49D82',
    'Raspi' : 'need to set',
    'Speed' : [9600, 115200],
}
dir_path = {
    'Mac' : {
        'cam' : f'{path_tpye['Mac']}{dataset_user['cam']}', # cam_frame
        'mctnn' : f'{path_tpye['Mac']}{dataset_user['mctnn']}', # detected_face_frame
        'embedding' : f'{path_tpye['Mac']}{dataset_user['embedding']}', # preprocessing_frame
        'comp_db' : f'{path_tpye['Mac']}{dataset_user['data_set']}' # recog_user
    },
    'Raspi' : {},
}