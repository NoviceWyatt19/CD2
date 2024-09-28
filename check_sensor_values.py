import serial
# import threading
import pandas as pd
import time

SERIAL_PATH = '/dev/cu.usbmodemF412FA6F49D82'
PORT_SPEED = 9600 # 115200 전송 데이터 형식이 밀릴 경우 바꾸기

ser = serial.Serial( 
    port=SERIAL_PATH,
    baudrate=PORT_SPEED,
    timeout= 2
)

values_db = []
sample_size = 100

def read_sensing_values(db, sampling_size, data_source):
    while len(db) < sampling_size:
        data_line = data_source.readline().decode().strip()

        if data_line:
            sensor_values = data_line.split( ',' ) # sensor_values = [value1, value2, value3]
            db.append( sensor_values )

            print( 10 * '-' +f'{len(db)}')
            print( f"value1(alcol) : {sensor_values[0]} \nvalue2(pir) : {sensor_values[1]} \nvalue3(heart) : {sensor_values[2]} \n\n" )

def save_db(db, file):
    df = pd.DataFrame(
        db,
        columns=['Sensor1', 'Sensor2', 'Sensor3'],
    )
    file_path = f'/Users/wyatt/Desktop/CD2_project/Sensor_db/{file}' # 라즈베리파이에서는 경로를 변경해야함
    df.to_csv( file_path, index= False)

    db.clear()

try:
    read_sensing_values(values_db, sample_size, ser)

    file_name = f'Sensor_data_{time.strftime("%m%d%H%M%S")}.csv'
    
    print( f'{len(values_db)}개의 데이터를 {file_name}에 저장하였습니다.' )
    save_db(values_db, file_name)
    
finally:
    ser.close()