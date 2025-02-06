from picarx import Picarx
import time

def continuous_rotate_and_scan(car: Picarx):
    total_duration = 7  # seconds for a full rotation
    start_time = time.time()
    end_time = start_time + total_duration
    
    scan_data = []
    
    # Start continuous rotation
    car.set_dir_servo_angle(30)  # Assuming 30 degrees is full right
    car.set_motor_speed(1, 50)  # Left wheel forward
    car.set_motor_speed(2, 50)  # Right wheel backward
    
    while time.time() < end_time:
        current_time = time.time() - start_time
        distance = car.ultrasonic.read()
        
        # Append data point
        scan_data.append((current_time, distance))
        
        # Optional: add a small delay to not overload the sensor or processor
        time.sleep(0.1)  # Adjust this delay as necessary
    
    # Stop the motors after full rotation
    car.stop()
    car.set_dir_servo_angle(0)  # Reset steering
    
    # Output or process the scan data
    for duration, dist in scan_data:
        print(f"Time: {duration:.2f}s, Distance: {dist:.2f}cm")

# Test the function
if __name__ == "__main__":
    car = Picarx()
    print("Starting continuous 360-degree scan...")
    continuous_rotate_and_scan(car)
    print("Scan complete.")