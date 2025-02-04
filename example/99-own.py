from picarx import Picarx
import readchar
from pydoc import text
from vilib import Vilib
from time import sleep, time, strftime, localtime
import threading
import os
from os import geteuid
from robot_hat import Music, TTS

if geteuid() != 0:
    print(f"\033[0;33m{'The program needs to be run using sudo, otherwise there may be no sound.'}\033[0m")


music = Music()
tts = TTS()

manual = '''
Press keys on keyboard to control the Car!
    w: Forward
    a: Turn wheels left
    s: Backward
    d: Turn wheels right
    i: Head up
    k: Head down
    j: Turn head left
    l: Turn head right
    t: TTS input
    b: beep horn
'''

def show_info(pan_angle: int, tilt_angle: int, servo_angle: int):
    print("\033[H\033[J",end='')  # clear terminal windows
    print(manual)
    print("Current driving angle: %d"%servo_angle)
    print("Current camera tilt angle: %d"%tilt_angle)
    print("Current camera pan angle: %d"%pan_angle)



def main():
    # Setting up the car to start
    pan_angle = 0
    tilt_angle = 0
    servo_angle = 0
    px = Picarx()
    show_info(pan_angle, tilt_angle, servo_angle)

    music.music_set_volume(20)
    tts.lang("en-US")

    music.sound_play_threading('../sounds/car-start-engine.wav')

    # Setting up the camera feed
    global flag_face, flag_color, qr_code_flag
    qrcode_thread = None

    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)


    while True:
        key = readchar.readkey()
        key = key.lower()
        if key in('wsadikjltb'): 
            match key:
                case 'w':
                    px.forward(80)
                case 's':
                    px.backward(80)
                case 'a':
                    servo_angle -= 10
                    if servo_angle<-30:
                        servo_angle=-30 
                case 'd':
                    servo_angle += 10
                    if servo_angle >= 30:
                        servo_angle = 30 
                case 'i':
                    tilt_angle+=5
                    if tilt_angle>30:
                        tilt_angle=30
                case 'k':
                    tilt_angle-=5
                    if tilt_angle<-30:
                        tilt_angle=-30
                case 'l':
                    pan_angle+=5
                    if pan_angle>30:
                        pan_angle=30
                case 'j':
                    pan_angle-=5
                    if pan_angle<-30:
                        pan_angle=-30
                case 't':
                    text = input("TTS input:\n")
                    tts.say(text)
                    sleep(0.05)
                case 'b':
                    music.sound_play_threading('../sounds/car-double-horn.wav')
                    sleep(0.05)
            px.set_dir_servo_angle(servo_angle)
            px.set_cam_tilt_angle(tilt_angle)
            px.set_cam_pan_angle(pan_angle)
            show_info(pan_angle, tilt_angle, servo_angle)

            sleep(0.2)
            px.forward(0)
        elif key == readchar.key.CTRL_C:
            px.forward(0)
            px.set_dir_servo_angle(0)
            px.set_cam_tilt_angle(0)
            px.set_cam_pan_angle(0)
            break

if __name__ == "__main__":
    main()

