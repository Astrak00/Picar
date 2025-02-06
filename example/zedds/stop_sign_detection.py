#!/usr/bin/env python3
import cv2
import numpy as np
import os
import time
from tflite_runtime.interpreter import Interpreter

from utils import load_labels

'''Global detection dictionary'''
traffic_sign_obj_parameter = {
    'x': 0,
    'y': 0,
    'w': 0,
    'h': 0,
    't': 'none',   # could be 'none', 'stop', 'right', 'left', 'forward'
    'acc': 0
}

'''Default model/labels'''
traffic_sign_model_path = "/opt/vilib/traffic_sign_150_dr0.2.tflite"
traffic_sign_labels_path = "/opt/vilib/traffic_sign_150_dr0.2_labels.txt"

def traffic_sign_predict(interpreter, img):
    '''
    Same as before:
    Resize + run inference => return (accuracy_float, label_idx).
    accuracy_float is 0.0 ~ 1.0
    '''
    _, model_width, model_height, model_depth = interpreter.get_input_details()[0]['shape']
    if model_depth not in (1, 3):
        raise ValueError('Unsupported model depth')

    # Resize to model shape
    resized = cv2.resize(img, (model_width, model_height), interpolation=cv2.INTER_LINEAR)
    reshaped = np.reshape(resized, (model_width, model_height, model_depth))
    input_data = np.expand_dims(reshaped, axis=0).astype('float32')

    # Perform inference
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
    # Return area of bounding box
    x, y, w, h = cv2.boundingRect(cnt)
    return w * h

def traffic_sign_detect(img, model=None, labels=None, border_rgb=(255, 0, 0)):
    '''
    The original logic that detects stop, left, right, forward, etc.
    We won't remove anything; it remains the same. 
    Then we update "traffic_sign_obj_parameter" with the largest sign found.
    '''
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

    # Convert border color from RGB -> BGR
    bgr_border = (border_rgb[2], border_rgb[1], border_rgb[0])

    # BGR -> HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Red color range
    mask_red1 = cv2.inRange(hsv, (157, 20, 20), (180, 255, 255))
    mask_red2 = cv2.inRange(hsv, (0,   20, 20), (10, 255, 255))
    # Blue color range
    mask_blue = cv2.inRange(hsv, (92, 10, 10), (125, 255, 255))

    # Combine
    mask_all = cv2.bitwise_or(mask_red1, mask_blue)
    mask_all = cv2.bitwise_or(mask_red2, mask_all)

    kernel_5 = np.ones((5,5), np.uint8)
    open_img = cv2.morphologyEx(mask_all, cv2.MORPH_OPEN, kernel_5, iterations=1)

    # Find contours
    _tuple = cv2.findContours(open_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(_tuple) == 3:
        _, contours, _ = _tuple
    else:
        contours, _ = _tuple
    contours = sorted(contours, key=cnt_area, reverse=False)

    max_area = 0
    traffic_sign_num = 0
    found_params = None

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 32 and h > 32:
            # If model is grayscale
            if model_depth == 1:
                region = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                region = img

            pad = 8
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(img.shape[1], x + w + pad)
            y2 = min(img.shape[0], y + h + pad)
            roi = region[y1:y2, x1:x2]

            # Scale [-1, 1]
            roi = roi / 255.0
            roi = (roi - 0.5) * 2.0

            # Predict
            acc_float, label_idx = traffic_sign_predict(interpreter, roi)
            acc_percent = int(round(acc_float * 100))
            label_name = loaded_labels[label_idx]

            # Only accept if >= 85% (adjust if needed)
            if acc_percent >= 85:
                area = w * h
                if area > max_area:
                    max_area = area
                    found_params = (x, y, w, h, label_name, acc_percent)
                    traffic_sign_num += 1

    # Update global dict
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

    return img  # We won't display it in headless mode


def main():
    """
    Headless loop that:
      1) Captures frames via PiCamera2
      2) Detects all sign types
      3) **Prints only if the sign is STOP**
    """
    print("Headless traffic-sign detection (only prints STOP)...")
    from picamera2 import Picamera2
    import libcamera

    picam2 = Picamera2()
    preview_config = picam2.preview_configuration
    preview_config.size = (640, 480)
    preview_config.format = 'RGB888'
    preview_config.transform = libcamera.Transform(hflip=False, vflip=False)
    preview_config.colour_space = libcamera.ColorSpace.Sycc()
    preview_config.buffer_count = 4
    preview_config.queue = True

    picam2.configure(preview_config)
    picam2.start()

    print("Press Ctrl+C to exit.\n")

    try:
        while True:
            # Capture in RGB
            frame_rgb = picam2.capture_array()
            # Convert to BGR for detection
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            # Run detection (all signs, but only print STOP)
            traffic_sign_detect(frame_bgr)
            sign_type = traffic_sign_obj_parameter['t']
            sign_acc  = traffic_sign_obj_parameter['acc']

            if sign_type == 'stop':
                print(f"STOP sign found at {sign_acc}% confidence")

            # small delay to reduce spam
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nExiting detection loop...")
    finally:
        picam2.stop()

if __name__ == "__main__":
    main()