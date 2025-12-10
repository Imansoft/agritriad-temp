# Updated directory paths as per guide.txt
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Folder paths
INPUT_AUDIO_DIR = os.path.join('audio', 'received')
OUTPUT_AUDIO_DIR = os.path.join('audio', 'send')
SENSOR_LOG_FILE = 'sensor_logs.txt'

# Ensure required folders exist
os.makedirs(INPUT_AUDIO_DIR, exist_ok=True)
os.makedirs(OUTPUT_AUDIO_DIR, exist_ok=True)

# Health check route
@app.route("/")
def health_check():
	return jsonify({"status": "ok"})

# WebSocket event: client connection
@socketio.on("connect")
def on_connect():
	print("A client connected")
	emit("server_message", {"msg": "Connected to server"})

# WebSocket event: client disconnection
@socketio.on("disconnect")
def on_disconnect():
	print("A client disconnected")

# WebSocket event: receive audio file
@socketio.on("upload_audio")
def handle_upload_audio(data):
	try:
		if "audio" not in data or "filename" not in data:
			emit("audio_error", {"error": "Missing audio or filename"})
			return
		audio_data = data["audio"]
		filename = secure_filename(data["filename"])
		save_path = os.path.join(INPUT_AUDIO_DIR, filename)
		# Assuming audio_data is base64 encoded
		with open(save_path, "wb") as f:
			import base64
			f.write(base64.b64decode(audio_data))
		emit("audio_response", {"status": "received", "filename": filename})
	except Exception as e:
		emit("audio_error", {"error": f"Failed to save file: {str(e)}"})

# WebSocket event: request audio file
@socketio.on("request_audio")
def handle_request_audio():
	try:
		filename = "English.wav"
		file_path = os.path.join(OUTPUT_AUDIO_DIR, filename)
		if not os.path.exists(file_path):
			emit("audio_error", {"error": f"File {filename} not found in {OUTPUT_AUDIO_DIR}"})
			return
		with open(file_path, "rb") as f:
			import base64
			audio_data = base64.b64encode(f.read()).decode("utf-8")
		emit("audio_response", {"audio": audio_data, "filename": filename})
	except Exception as e:
		emit("audio_error", {"error": f"Failed to read file: {str(e)}"})

# WebSocket event: receive sensor data
@socketio.on("log_sensor_data")
def handle_log_sensor_data(data):
	try:
		required_fields = ["device_id", "timestamp", "light_value", "moisture_value"]
		if not all(field in data for field in required_fields):
			emit("database_error", {"error": "Missing required sensor fields"})
			return
		with open(SENSOR_LOG_FILE, "a", encoding="utf-8") as f:
			f.write(json.dumps(data) + "\n")
		emit("database_response", {"status": "saved"})
	except Exception as e:
		emit("database_error", {"error": f"Failed to log sensor data: {str(e)}"})

# WebSocket event: fetch sensor data
@socketio.on("fetch_sensor_data")
def handle_fetch_sensor_data(data):
	try:
		count = data.get("count", 1)
		if not isinstance(count, int) or count < 1:
			emit("database_error", {"error": "Count must be a positive integer"})
			return
		
		if not os.path.exists(SENSOR_LOG_FILE):
			emit("database_error", {"error": "No sensor data available"})
			return
		
		with open(SENSOR_LOG_FILE, "r", encoding="utf-8") as f:
			lines = f.readlines()
		
		total_entries = len(lines)
		if total_entries == 0:
			emit("database_error", {"error": "No sensor data available"})
			return
		
		if count > total_entries:
			selected = [json.loads(line) for line in lines[-total_entries:]]
			message = f"max data in DB is {total_entries}"
		else:
			selected = [json.loads(line) for line in lines[-count:]]
			message = None
		
		response = {
			"entries_returned": len(selected),
			"data": selected
		}
		if message:
			response["message"] = message
		
		emit("database_response", response)
	except Exception as e:
		emit("database_error", {"error": f"Failed to read sensor log: {str(e)}"})


# Run the Flask-SocketIO server
if __name__ == "__main__":
	socketio.run(app, host="0.0.0.0", port=5000, debug=True)
