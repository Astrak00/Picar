var server_port = 5000;
var server_addr = "http://localhost";

// send commands
function sendCommand(command) {
    fetch(`${server_addr}:${server_port}/move`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: command })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Car Response:", data);
        document.getElementById("command-response").innerText = "Car Response: " + JSON.stringify(data, null, 2);
    })
    .catch(error => console.error("Error:", error));
}

// sensor data to HTML
function displaySensorData(data) {
    return `
    <div class="sensor-cards">
      <div class="sensor-card">
        <h3>Ultrasonic Distance</h3>
        <p>${data.ultrasonic_distance ? data.ultrasonic_distance + " cm" : "N/A"}</p>
      </div>
      <div class="sensor-card">
        <h3>Cliff Status</h3>
        <p>${data.cliff_status ? data.cliff_status : "N/A"}</p>
      </div>
      <div class="sensor-card">
        <h3>Stop Sign Detected</h3>
        <p>${data.stop_sign_detected ? "Yes" : "No"}</p>
      </div>
    </div>
    `;
}

function getSensorData() {
    fetch(`${server_addr}:${server_port}/sensor_data`)
        .then(response => response.json())
        .then(data => {
            console.log("Sensor Data:", data);
            document.getElementById("sensor-display").innerHTML = displaySensorData(data);
        })
        .catch(error => console.error("Sensor Error:", error));
}

// fetch sensor data every second
setInterval(getSensorData, 1000);

function greeting(){
    var name = document.getElementById("myName").value;
    document.getElementById("greet").innerHTML = "Hello " + name + " !";

    fetch(`${server_addr}:${server_port}/greet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("greet_from_server").innerText = data.server_greet;
    })
    .catch(error => console.error("Error:", error));
}

// listeners
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("forward-btn").addEventListener("click", () => sendCommand("w"));
    document.getElementById("left-btn").addEventListener("click", () => sendCommand("a"));
    document.getElementById("backward-btn").addEventListener("click", () => sendCommand("s"));
    document.getElementById("right-btn").addEventListener("click", () => sendCommand("d"));
    document.getElementById("stop-btn").addEventListener("click", () => sendCommand("stop"));
});