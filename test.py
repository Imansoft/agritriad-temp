import socketio
import base64
import os
import time

# Create a Socket.IO client
sio = socketio.Client()

# Server URL
SERVER_URL = "https://agritriad-temp.onrender.com" #"http://127.0.0.1:5000"

# Event handlers
@sio.event
def connect():
    print("Connected to server")

@sio.event
def server_message(data):
    print(f"Server message: {data}")

@sio.event
def audio_response(data):
    if "audio" in data:
        # Received audio file
        audio_data = base64.b64decode(data["audio"])
        filename = data.get("filename", "received_audio.wav")
        with open(filename, "wb") as f:
            f.write(audio_data)
        print(f"Audio response received and saved as {filename}")
    else:
        print(f"Audio response: {data}")

@sio.event
def audio_error(data):
    print(f"Audio error: {data}")

@sio.event
def database_response(data):
    print(f"Database response: {data}")

@sio.event
def database_error(data):
    print(f"Database error: {data}")

@sio.event
def disconnect():
    print("Disconnected from server")

# Test functions
def test_upload_audio(audio_path):
    """Upload audio file to server"""
    if not os.path.exists(audio_path):
        print(f"Audio file {audio_path} not found")
        return
    
    with open(audio_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")
    
    filename = os.path.basename(audio_path)
    sio.emit("upload_audio", {"audio": audio_data, "filename": filename})
    print(f"Uploaded audio: {filename}")
    time.sleep(1)  # Wait for response

def test_request_audio():
    """Request audio file from server"""
    sio.emit("request_audio")
    print("Requested audio from server")
    time.sleep(1)  # Wait for response

def test_log_sensor_data(device_id, light_value, moisture_value):
    """Send sensor data to server"""
    from datetime import datetime
    data = {
        "device_id": device_id,
        "timestamp": datetime.now().isoformat(),
        "light_value": light_value,
        "moisture_value": moisture_value
    }
    sio.emit("log_sensor_data", data)
    print(f"Logged sensor data: {data}")
    time.sleep(1)  # Wait for response

def test_fetch_sensor_data(count=1):
    """Fetch sensor data from server"""
    sio.emit("fetch_sensor_data", {"count": count})
    print(f"Requested {count} sensor entries")
    time.sleep(1)  # Wait for response

if __name__ == "__main__":
    try:
        # Connect to server
        sio.connect(SERVER_URL)
        time.sleep(1)
        
        # Uncomment the test you want to run
        
        # Test 1: Upload audio
        # test_upload_audio("audio/send/English.wav")
        
        # Test 2: Request audio
        test_request_audio()
        
        # Test 3: Log sensor data
        # test_log_sensor_data("AGRO-001", 320, 690)
        
        # Test 4: Fetch sensor data
        # test_fetch_sensor_data(1)
        # test_fetch_sensor_data(2)
        # test_fetch_sensor_data(14)
        
        # Keep connection alive
        time.sleep(3)
        sio.disconnect()
        
    except Exception as e:
        print(f"Error: {e}")
