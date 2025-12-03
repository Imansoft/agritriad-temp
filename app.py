
# Updated directory paths as per guide.txt
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
CORS(app)

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

# 1. /api/audio (POST): Receive audio file from hardware
@app.route("/api/audio", methods=["POST"])
def receive_audio():
	# Check if the request has the file part
	if 'audio' not in request.files:
		return jsonify({"error": "No audio file part in the request"}), 400
	file = request.files['audio']
	if file.filename == '':
		return jsonify({"error": "No selected file"}), 400
	filename = secure_filename(file.filename)
	save_path = os.path.join(INPUT_AUDIO_DIR, filename)
	try:
		file.save(save_path)
	except Exception as e:
		return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
	return jsonify({"status": "received", "filename": filename})


# 2. /api/audio2 (GET): Return a fixed audio file to hardware
@app.route("/api/audio2", methods=["GET"])
def send_audio():
	# Always return 'English.wav' from audio/sent
	filename = "English.wav"
	file_path = os.path.join(OUTPUT_AUDIO_DIR, filename)
	if not os.path.exists(file_path):
		return jsonify({"error": f"File {filename} not found in {OUTPUT_AUDIO_DIR}"}), 404
	return send_from_directory(OUTPUT_AUDIO_DIR, filename, mimetype="audio/wav")

# 3. /api/database (POST): Receive sensor readings as JSON
@app.route("/api/database", methods=["POST"])
def receive_sensor_data():
	if not request.is_json:
		return jsonify({"error": "Request must be JSON"}), 400
	data = request.get_json()
	# Basic validation for required fields
	required_fields = ["device_id", "timestamp", "light_value", "moisture_value"]
	if not all(field in data for field in required_fields):
		return jsonify({"error": "Missing required sensor fields"}), 400
	try:
		with open(SENSOR_LOG_FILE, "a", encoding="utf-8") as f:
			f.write(json.dumps(data) + "\n")
	except Exception as e:
		return jsonify({"error": f"Failed to log sensor data: {str(e)}"}), 500
	return jsonify({"status": "saved"})

# Run the Flask server
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
