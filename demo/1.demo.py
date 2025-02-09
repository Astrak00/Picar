from picarx import Picarx
import time
from robot_hat import Music, TTS

DIRECTION_STEP = 10
DIRECTION_MAX = 30
SAFE_DISTANCE = 40
DANGER_DISTANCE = SAFE_DISTANCE // 2
MOVE_POWER = 50
POWER = MOVE_POWER 

music = Music()
tts = TTS()

if __name__ == "__main__":
    
    try:
        px = Picarx()
        tts.lang("en-US")

        # Test the direction servo range
        for angle in range(-DIRECTION_MAX, DIRECTION_MAX+1, DIRECTION_STEP):
            px.set_dir_servo_angle(angle)
            px.set_cam_tilt_angle(angle)
            px.set_cam_pan_angle(angle)
            time.sleep(0.3)

        px.set_cam_tilt_angle(0)
        px.set_cam_pan_angle(0)
        px.set_dir_servo_angle(0)
        px.forward(MOVE_POWER * 2)
        time.sleep(0.3)
        px.backward(MOVE_POWER * 2)
        time.sleep(0.3)
        px.stop()
        
        input_txt = ""
        while input_txt.lower() != "y":
            input_txt = input("Ready for the obstacle avoidance test? (y/n): ")

        bonk_times = 0
        start = time.time()
        # Run for 20 seconds
        while time.time() - start < 20:
            distance = round(px.ultrasonic.read(), 2)
            if distance >= SAFE_DISTANCE:
                print(f"Safe distance. Moving forward. {distance}")
                px.set_dir_servo_angle(0)
                px.forward(POWER)

            elif distance >= DANGER_DISTANCE:
                print(f"Danger distance. Moving forward. {distance}")
                px.set_dir_servo_angle(-30)  # slight left turn
                px.forward(POWER)
                time.sleep(0.2)

            else:
                print(f"Too close. Backing up to the right. {distance}")
                bonk_times += 1

                px.stop()
                time.sleep(0.2)

                px.set_dir_servo_angle(30)

                px.backward(POWER*2)
                time.sleep(1.0)

                px.stop()
                px.set_dir_servo_angle(0)
                px.forward(POWER)
                time.sleep(0.2)

    finally:
        print(f"Times beeped {bonk_times}")
        px.stop()
        px.set_dir_servo_angle(0)
