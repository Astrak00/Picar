"""
    Cliff detection and ultrasonic distance control program for Picar-X:
"""

from picarx import Picarx
from time import sleep
from robot_hat import TTS
import time

tts = TTS()
tts.lang("en-US")

px = Picarx()
px.set_cliff_reference([200, 200, 200])

current_state = None
px_power = 10
offset = 20
last_state = "safe"

POWER = 50
SafeDistance = 40   # > 40 safe
DangerDistance = 20 # > 20 && < 40 turn around, 
                    # < 20 backward

def main():
    try:
        while True:
            gm_val_list = px.get_grayscale_data()
            gm_state = px.get_cliff_status(gm_val_list)
            if gm_state:
                state = "danger"   
                px.backward(40)
                if last_state == "safe":
                    tts.say("danger")
                    sleep(0.1)
            else:
                state = "safe"
                px.stop()
                distance = round(px.ultrasonic.read(), 2)
                print("distance: ", distance)
                if distance >= SafeDistance:
                    px.set_dir_servo_angle(0)
                    px.forward(POWER)
                elif distance >= DangerDistance:
                    px.set_dir_servo_angle(30)
                    px.forward(POWER)
                    time.sleep(0.1)
                else:
                    px.set_dir_servo_angle(-30)
                    px.backward(POWER)
                    time.sleep(0.5)
            last_state = state

    finally:
        px.stop()
        print("stop and exit")
        sleep(0.1)

if __name__ == "__main__":
    main()