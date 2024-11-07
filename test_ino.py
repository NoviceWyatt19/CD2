import serial
import configuration as con

ser = serial.Serial( 
    port=con.ser_setting['Mac'],
    baudrate=con.ser_setting['Speed'][0],
    timeout= 2
)

cnt = 0
while True:
    given = ser.readline().decode()
    print(f"{cnt}: {given}")
    cnt += 1