import serial
import threading
import pandas as pd
import time

SERIAL_PATH = '/dev/ttyUSB0'
PORT_SPEED = 9600 # 115200 전송 데이터 형식이 밀릴경우 바꾸기

ser = serial.Serial( SERIAL_PATH, PORT_SPEED, timeout=2 )

values_db = []
sample_size = 100

with open( 'sensor_data.csv', 'a' ) as f:
    
    try:
        while True:
            line = ser.readline().decode().strip()

            if line:
                
                sensor_values = line.split( ',' ) # sensor_values = [value1, value2, value3]
                values_db.append( sensor_values )

                print( 10 * '-' )
                print( f"value1 : {sensor_values[0]} \n value2 : {sensor_values[1]} \n value3 : {sensor_values[2]} \n\n" )
                

                if len(values_db) >= sample_size:
                    
                    file_name = f'Sensor_data_{time.strftime("%m%d%H%M%S")}.csv'
                    
                    df = pd.DataFrame( values_db, columns=['Sensor1', 'Sensor2', 'Sensor3'] )
                    df.to_csv( file_name, index=False )
                    
                    print( f'{len(values_db)}개의 데이터를 {file_name}에 저장하였습니다.' )
                    values_db.clear()
    finally:
        ser.closr()