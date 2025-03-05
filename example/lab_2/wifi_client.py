import socket
import json
import time

HOST = "10.12.8.139"
PORT = 65431

def send_command(command):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.send(command.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response

while True:
    cmd = input("Enter command (sensor, w, a, s, d, stop, or q to quit): ").lower().strip()
    if cmd == 'q':
        break
    if cmd == "sensor":
        print("Reading car sensors")
        try:
            while True:
                response = send_command("status")
                try:
                    data = json.loads(response)
                    print("Sensor data:")
                    for key, value in data.items():
                        print(f"{key.replace('_', ' ').capitalize()}: {value}")
                except Exception:
                    print(response)
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped sensor readings")
    else:
        response = send_command(cmd)
        print(response)