import serial
import configuration as con
import keyboard

ser = serial.Serial(con.ser_setting['Mac'])

# 상태 초기화
face_check: bool = True
eye_detect: bool = True
user_recog: bool = True
full_stack: bool = False

while True:
    # 상태에 따른 명령어 업데이트
    eye_part = "True" if face_check and eye_detect else "False"
    face_part = "True" if face_check and user_recog and full_stack else "False"
    stack_state = 'DONE' if full_stack else 'NULL'
    oper_code = f"<EYE>{eye_part}_<FACE>{stack_state}"

    # Arduino에 명령어 전송
    ser.write(oper_code.encode())

    # 키보드 입력에 따라 상태 조정
    if keyboard.is_pressed('e'):
        eye_detect = not eye_detect
    if keyboard.is_pressed('r'):
        user_recog = not user_recog
    if keyboard.is_pressed('f'):
        face_check = not face_check
    if keyboard.is_pressed('a'):
        full_stack = True

    # q가 눌리면 모든 상태를 초기화
    if keyboard.is_pressed('q'):
        face_check = True
        eye_detect = True
        user_recog = True
        full_stack = False
        print("All states have been reset.")

    # 최종 결과 송신
    if full_stack:
        pass_code = 1 if face_check and user_recog and eye_detect else 0
        oper_code = f"FINALL_{pass_code}"
        ser.write(oper_code.encode())
        break
