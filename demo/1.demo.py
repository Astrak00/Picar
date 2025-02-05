from picarx import Picarx
import time
from robot_hat import Music,TTS

DIRECTION_STEP = 10
DIRECTION_MAX = 30
SAFE_DISTANCE = 40
DANGER_DISTANCE = SAFE_DISTANCE // 2
MOVE_POWER = 50
POWER = MOVE_POWER 

OBSTACLE_DETECTED_MSG = "Obstacle detected. Turning around."

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
        px.forward(0)
        px.stop()
        px.stop()
        
        input_txt = ""
        while input_txt.lower() != "y":
            input_txt = input("Reaady fot the obstacle avoidance test? (y/n): ")

        times_beeped = 0
        start = time.time()
        while time.time() - start < 20 and times_beeped < 10:
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ", distance)
            if distance >= SAFE_DISTANCE:
                px.set_dir_servo_angle(0)
                px.forward(POWER)
            elif distance >= DANGER_DISTANCE // 2:
                px.set_dir_servo_angle(30)
                px.forward(POWER)
                time.sleep(0.2)
            else:
                px.set_dir_servo_angle(-30)
                music.sound_play_threading('../sounds/car-double-horn.wav')
                times_beeped += 1
                #tts.say(OBSTACLE_DETECTED_MSG)
                time.sleep(0.5)
                px.backward(POWER)

    finally:
        print(f"Times beeped {times_beeped}")
        px.forward(0)

        
