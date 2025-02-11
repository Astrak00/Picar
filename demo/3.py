from picarx import Picarx
import time
import matplotlib.pyplot as plt
import numpy as np

DIRECTION_STEP = 10  # Angle step for scanning
DIRECTION_MAX = 60   # Maximum pan angle for scanning
SAFE_DISTANCE = 50   # Safe distance threshold in cm
OBSTACLE_DETECTION_DISTANCE = 25
DIVISION_CONSTANT = 1


class Car():
    def __init__(self, dimensions: tuple[int, int]):
        self.px = Picarx()
        self.scan_data = None
        self.pos_x = 50
        self.pos_y = 50
        self.angle = 0
        self.map = np.zeros(dimensions)


def scan_environment(car: Car) -> dict:
    """Scans the environment using the ultrasonic sensor and returns a mapping of distances."""
    scan_data = {}

    for angle in range(-DIRECTION_MAX, DIRECTION_MAX + 1, DIRECTION_STEP):
        car.px.set_cam_pan_angle(angle)
        time.sleep(0.2)  # Allow time for sensor to stabilize
        distance = round(car.px.ultrasonic.read(), 2) / DIVISION_CONSTANT
        
        if distance <= 0:
            distance = -2
        scan_data[angle] = distance
        print(f"Angle: {angle}°, Distance: {distance} cm")


    for i in scan_data.keys():
        if scan_data[i] <= SAFE_DISTANCE / DIVISION_CONSTANT and scan_data[i] > 0:
            obstacle_position = (car.pos_x + int(scan_data[i] * np.cos(np.radians(i))), car.pos_y + int(scan_data[i] * np.sin(np.radians(i))))
            print(f"Obstacle detected at {obstacle_position}")
            car.map[obstacle_position] = 1
        # If two points are close enough **between them**, we interpolate also have the points in between the two points as obstacles
        for i in range(-DIRECTION_MAX, DIRECTION_MAX, DIRECTION_STEP):
            if scan_data[i] <= SAFE_DISTANCE / DIVISION_CONSTANT and scan_data[i] > 0:
                next_angle = i + DIRECTION_STEP
                if next_angle in scan_data and scan_data[next_angle] <= SAFE_DISTANCE / DIVISION_CONSTANT and scan_data[next_angle] > 0:
                    x1, y1 = car.pos_x + int(scan_data[i] * np.cos(np.radians(i))), car.pos_y + int(scan_data[i] * np.sin(np.radians(i)))
                    x2, y2 = car.pos_x + int(scan_data[next_angle] * np.cos(np.radians(next_angle))), car.pos_y + int(scan_data[next_angle] * np.sin(np.radians(next_angle)))
                    num_points = max(abs(x2 - x1), abs(y2 - y1))
                    if num_points != 0:
                        for j in range(num_points + 1):
                            x = x1 + j * (x2 - x1) // num_points
                            y = y1 + j * (y2 - y1) // num_points
                            car.map[x, y] = 1
        
            
    car.px.set_cam_pan_angle(0)  # Reset camera to center
    return scan_data

def plot_scan(scan_data: dict, car: Car):
    """Plots the scanned environment using polar coordinates."""
    angles = np.radians(list(scan_data.keys()))
    distances = list(scan_data.values())

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    ax.plot(angles, distances, marker='o', linestyle='-', color='b', label="Obstacle Map")
    ax.fill(angles, distances, color='b', alpha=0.2)
    ax.set_title("Ultrasonic Sensor Mapping")
    ax.legend()
    plt.show()
    # Save the plot as a PNG file
    plt.savefig("environment_scan.png")

if __name__ == "__main__":
    try:
        dimensions = (200, 200)
        car = Car(dimensions=dimensions)

        print("Starting environment scan...")
        scan_data = scan_environment(car)

        print("Scan complete. Plotting data...")
        plot_scan(scan_data, car)

        print("Plot saved as 'environment_scan.png'")

        # car.map[car.pos_x, car.pos_y] = 7
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                car.map[car.pos_x + dx, car.pos_y + dy] = 7
        map_list = car.map.tolist()
        np.savetxt('map.txt', map_list, fmt='%d')


    finally:
        car.px.set_cam_pan_angle(0)
        car.px.forward(0)
        car.px.stop()
