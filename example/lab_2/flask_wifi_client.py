from flask import Flask, request, jsonify
import socket
import json
import time

app = Flask(__name__)

HOST = "172.16.255.205"
PORT = 65431

def send_command(command):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.send(command.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    command = data.get("command")
    if command not in ["w", "a", "s", "d", "stop"]:
        return jsonify({"error": "Invalid command"}), 400
    result = send_command(command)
    return jsonify({"result": result})

@app.route('/sensor_data', methods=['GET'])
def sensor_data():
    result = send_command("status")
    try:
        data = json.loads(result)
        return jsonify(data)
    except Exception:
        return jsonify({"error": "Failed to parse sensor data", "raw_response": result}), 500

@app.route('/')
def index():
    return "Flask API for Car Control is running. Use /move and /sensor_data endpoints."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
