import socket
import json
import time
from picarx import Picarx
import cv2
import numpy as np
import os
from tflite_runtime.interpreter import Interpreter
from picamera2 import Picamera2
import libcamera
from utils import load_labels

traffic_sign_obj_parameter = {
    'x': 0,
    'y': 0,
    'w': 0,
    'h': 0,
    't': 'none',
    'acc': 0
}

traffic_sign_model_path = "/opt/vilib/traffic_sign_150_dr0.2.tflite"
traffic_sign_labels_path = "/opt/vilib/traffic_sign_150_dr0.2_labels.txt"

px = Picarx()

picam2_stop = Picamera2()
stop_config = picam2_stop.preview_configuration
stop_config.size = (640, 480)
stop_config.format = 'RGB888'
stop_config.transform = libcamera.Transform(hflip=False, vflip=False)
stop_config.colour_space = libcamera.ColorSpace.Sycc()
stop_config.buffer_count = 1
picam2_stop.configure(stop_config)
picam2_stop.start()

def traffic_sign_predict(interpreter, img):
    _, model_width, model_height, model_depth = interpreter.get_input_details()[0]['shape']
    if model_depth not in (1, 3):
        raise ValueError('Unsupported model depth')
    resized = cv2.resize(img, (model_width, model_height), interpolation=cv2.INTER_LINEAR)
    reshaped = np.reshape(resized, (model_width, model_height, model_depth))
    input_data = np.expand_dims(reshaped, axis=0).astype('float32')
    input_index = interpreter.get_input_details()[0]['index']
    interpreter.set_tensor(input_index, input_data)
    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output_data = interpreter.get_tensor(output_details['index'])
    result = np.squeeze(output_data)
    accuracy = float(np.max(result))
    label_idx = np.argmax(result)
    return accuracy, label_idx

def cnt_area(cnt):
    x, y, w, h = cv2.boundingRect(cnt)
    return w * h

def traffic_sign_detect(img, model=None, labels=None, border_rgb=(255, 0, 0)):
    # Detect traffic signs in the given image and update traffic_sign_obj_parameter
    if model is None:
        model = traffic_sign_model_path
    if labels is None:
        labels = traffic_sign_labels_path
    if not os.path.exists(model):
        print("[ERROR] Model path not found:", model)
        return img
    if not os.path.exists(labels):
        print("[ERROR] Labels file not found:", labels)
        return img
    loaded_labels = load_labels(labels)
    interpreter = Interpreter(model)
    interpreter.allocate_tensors()
    model_depth = interpreter.get_input_details()[0]['shape'][3]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask_red1 = cv2.inRange(hsv, (157, 20, 20), (180, 255, 255))
    mask_red2 = cv2.inRange(hsv, (0, 20, 20), (10, 255, 255))
    mask_blue = cv2.inRange(hsv, (92, 10, 10), (125, 255, 255))
    mask_all = cv2.bitwise_or(mask_red1, mask_blue)
    mask_all = cv2.bitwise_or(mask_red2, mask_all)
    kernel_5 = np.ones((5, 5), np.uint8)
    open_img = cv2.morphologyEx(mask_all, cv2.MORPH_OPEN, kernel_5, iterations=1)
    _tuple = cv2.findContours(open_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(_tuple) == 3:
        _, contours, _ = _tuple
    else:
        contours, _ = _tuple
    contours = sorted(contours, key=cnt_area, reverse=False)
    max_area = 0
    found_params = None
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 32 and h > 32:
            region = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if model_depth == 1 else img
            pad = 8
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(img.shape[1], x + w + pad)
            y2 = min(img.shape[0], y + h + pad)
            roi = region[y1:y2, x1:x2]
            roi = roi / 255.0
            roi = (roi - 0.5) * 2.0
            acc_float, label_idx = traffic_sign_predict(interpreter, roi)
            acc_percent = int(round(acc_float * 100))
            label_name = loaded_labels[label_idx]
            if acc_percent >= 85:
                area = w * h
                if area > max_area:
                    max_area = area
                    found_params = (x, y, w, h, label_name, acc_percent)
    if found_params:
        x, y, w, h, label_name, acc_val = found_params
        traffic_sign_obj_parameter['x'] = x + w // 2
        traffic_sign_obj_parameter['y'] = y + h // 2
        traffic_sign_obj_parameter['w'] = w
        traffic_sign_obj_parameter['h'] = h
        traffic_sign_obj_parameter['t'] = label_name
        traffic_sign_obj_parameter['acc'] = acc_val
    else:
        traffic_sign_obj_parameter['x'] = 0
        traffic_sign_obj_parameter['y'] = 0
        traffic_sign_obj_parameter['w'] = 0
        traffic_sign_obj_parameter['h'] = 0
        traffic_sign_obj_parameter['t'] = 'none'
        traffic_sign_obj_parameter['acc'] = 0
    return img

def detect_stop_sign():
    frame_rgb = picam2_stop.capture_array()
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    traffic_sign_detect(frame_bgr)
    if traffic_sign_obj_parameter['t'].lower() == 'stop' and traffic_sign_obj_parameter['acc'] >= 85:
        return True
    return False


# _________________________ All Stop Sign Detection Above _________________________



def move_car(command):
    speed = 50
    if command == "w":
        px.forward(speed)
        time.sleep(1)
        px.stop()
        return "Moved forward for 1 second"
    elif command == "s":
        px.backward(speed)
        time.sleep(1)
        px.stop()
        return "Moved backward for 1 second"
    elif command == "a":
        px.set_dir_servo_angle(-30)
        px.forward(speed)
        time.sleep(1)
        px.stop()
        return "Turned left for 1 second"
    elif command == "d":
        px.set_dir_servo_angle(30)
        px.forward(speed)
        time.sleep(1)
        px.stop()
        return "Turned right for 1 second"
    elif command == "stop":
        px.stop()
        return "Car stopped"
    else:
        return "Invalid movement command"

def get_sensor_data():
    try:
        distance = round(px.ultrasonic.read(), 2)
    except Exception:
        distance = None
    try:
        gm_val_list = px.get_grayscale_data()
        cliff_status = px.get_cliff_status(gm_val_list)
    except Exception:
        gm_val_list, cliff_status = None, None
    try:
        stop_sign = detect_stop_sign()
    except Exception:
        stop_sign = None
    sensor_data = {
        "ultrasonic_distance": distance,
        "gray_scale": gm_val_list,
        "cliff_status": "danger" if cliff_status else "safe",
        "stop_sign_detected": stop_sign
    }
    return sensor_data

HOST = '0.0.0.0'
PORT = 65431

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server listening on {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connected by {client_address}")
    data = client_socket.recv(1024).decode().strip()
    if not data:
        client_socket.close()
        continue
    print(f"Received: {data}")
    if data.lower() == "status":
        sensor_data = get_sensor_data()
        response = json.dumps(sensor_data)
    elif data.lower() in ["w", "a", "s", "d", "stop"]:
        response = move_car(data.lower())
    else:
        response = f"Received command: {data}"
    client_socket.send(response.encode())
    client_socket.close()