from picarx import Picarx
import readchar
from pydoc import text
from vilib import Vilib
from time import sleep, time, strftime, localtime
import threading
import os
from os import geteuid
from robot_hat import Music, TTS
import numpy as np
from enum import Enum


class Direction(Enum):
    FORWARD = 1
    BACKWARD = 2


class Car():
    def __init__(self, dimensions: tuple[int, int], pos_x: int, pos_y: int, car: Picarx):
        if len(dimensions) != 2:
            raise ValueError("The dimensions must be a tuple with two integers.")
        if pos_x < 0 or pos_x >= dimensions[0]:
            raise ValueError("The x position must be between 0 and the first dimension.")
        if pos_y < 0 or pos_y >= dimensions[1]:
            raise ValueError("The y position must be between 0 and the second dimension.")

        self.map = np.zeros(dimensions)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.px = car




if geteuid() != 0:
    print(f"\033[0;33m{'The program needs to be run using sudo, otherwise there may be no sound.'}\033[0m")

MOVEMENT_STEP = 20
MOVEMENT_STEP_TO_CM = 1/4.5
DIRECTION_STEP = 10
DIRECTION_MAX = 30
SCAN_DISTANCE = MOVEMENT_STEP

CAMERA_PAN_STEP = 5
CAMERA_TILT_STEP = 5
MAX_PAN_CAMERA_ANGLE = 60

INSTRUCTION_DELAY = 0.05

OBSTACLE_DETECTION_DISTANCE = 10
DANGER_DISTANCE = 20
OBSTACLE_MESSAGE = "Obstacle detected. Turning around."


music = Music()
tts = TTS()


pan_angle = 0
tilt_angle = 0
servo_angle = 0

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
    x: Scan the area
'''

def show_info(pan_angle: int, tilt_angle: int, servo_angle: int, car: Picarx):
    print("\033[H\033[J",end='')  # clear terminal windows
    print(manual)
    print("Current driving angle: %d"%servo_angle)
    print("Current camera tilt angle: %d"%tilt_angle)
    print("Current camera pan angle: %d"%pan_angle)
    print("Ultrasonic distance: %.2f cm"%car.ultrasonic.read())



def move(car: Car, direction: Direction, step: int = MOVEMENT_STEP):
    movement_step = step//MOVEMENT_STEP

    if direction == Direction.FORWARD:
        distance = round(car.px.ultrasonic.read(), 2)
        if distance <= DANGER_DISTANCE:
            tts.say(OBSTACLE_MESSAGE)
            return
        if distance <= OBSTACLE_DETECTION_DISTANCE:
            # TODO: Add the obstacle to the map following the video
            pass
        if car.pos_y + movement_step < car.map.shape[1]:
            car.pos_y += movement_step
            car.px.forward(step)

    elif direction == Direction.BACKWARD:
        if car.pos_y - movement_step >= 0:
            car.pos_y -= movement_step
            car.px.backward(step)


def scan(car: Car):
    # The idea is to scan the are in front of the car
    # Turn the camera from -60 to 60 degrees and get the distance with the ultrasonic sensor

    # Set up the camera to a horizontal position
    car.px.backward(SCAN_DISTANCE)

    # Iterate from -60 to 60 degrees
    for i in range(-DIRECTION_MAX, DIRECTION_MAX+1, DIRECTION_STEP):
        car.px.forward(SCAN_DISTANCE)
        car.px.set_dir_servo_angle(i)
        distance = round(car.px.ultrasonic.read(), 2) # This distance is in cm
        # Knowing the distance and the angle, we can calculate the position of the obstacle in the map
        if distance <= OBSTACLE_DETECTION_DISTANCE:
            obstacle_position = (car.pos_x + int(distance * np.cos(np.radians(i))), car.pos_y + int(distance * np.sin(np.radians(i))))
            car.map[obstacle_position] = 1
        sleep(INSTRUCTION_DELAY)
        sleep(2)
        car.px.backward(SCAN_DISTANCE)
        
        # Clear the terminal and show the map
        print("\033[H\033[J",end='')
        print(car.map)
        sleep(2)

    # Mark the car position in the map as a 7
    car.map[car.pos_x, car.pos_y] = 7
    # Conver the map to a list of lists
    map_list = car.map.tolist()
    # Save the map to a file
    np.savetxt('map.txt', map_list, fmt='%d')


def main():
    global pan_angle, tilt_angle, servo_angle
    # Setting up the car to start
    print(pan_angle)
    px = Picarx()

    music.music_set_volume(20)
    tts.lang("en-US")

    # music.sound_play_threading('../sounds/car-start-engine.wav')

    # Setting up the camera feed
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)

    car = Car(
        dimensions=(20,20),
        pos_x=10,
        pos_y=10,
        car=px
    )
    show_info(pan_angle, tilt_angle, servo_angle, px)

    try:
        while True:
            key = readchar.readkey()
            key = key.lower()
            if key in('wsadikjltbx'):
                match key:
                    case 'w':
                        car.px.forward(MOVEMENT_STEP)
                    case 's':
                        car.px.backward(MOVEMENT_STEP)
                    case 'a':
                        servo_angle -= 10
                        if servo_angle<-DIRECTION_MAX:
                            servo_angle=-DIRECTION_MAX
                    case 'd':
                        servo_angle += 10
                        if servo_angle >= DIRECTION_MAX:
                            servo_angle = DIRECTION_MAX
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
                        #sleep(0.05)
                    case 'b':
                        tts.sound_play_threading('../sounds/car-double-horn.wav')
                        sleep(0.05)
                    case 'x':
                        scan(car)
                car.px.set_dir_servo_angle(servo_angle)
                car.px.set_cam_tilt_angle(tilt_angle)
                car.px.set_cam_pan_angle(pan_angle)
                show_info(pan_angle, tilt_angle, servo_angle, px)
                sleep(0.2)
                car.px.forward(0)
            elif key == readchar.key.CTRL_C:
                car.px.forward(0)
                car.px.set_dir_servo_angle(0)
                car.px.set_cam_tilt_angle(0)
                car.px.set_cam_pan_angle(0)
                return
            else:
                show_info(pan_angle, tilt_angle, servo_angle, px)
            show_info(pan_angle, tilt_angle, servo_angle, px)
    except KeyboardInterrupt:
        car.px.forward(0)
        car.px.set_dir_servo_angle(0)
        car.px.set_cam_tilt_angle(0)
        car.px.set_cam_pan_angle(0)
        Vilib.camera_stop()
        print("\n\033[0;31m{'The program was stopped by the user.'}\033[0m")
        return

if __name__ == "__main__":
    main()
