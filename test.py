import requests
import base64
import os
import time
from datetime import datetime

# Server URL
SERVER_URL = "http://127.0.0.1:5000" # "https://agritriad-temp.onrender.com"  # "http://127.0.0.1:5000"

# Test functions
def test_upload_audio(audio_path):
	"""Upload audio file to server"""
	if not os.path.exists(audio_path):
		print(f"Audio file {audio_path} not found")
		return
	
	with open(audio_path, "rb") as f:
		files = {'audio': f}
		response = requests.post(f"{SERVER_URL}/api/audio", files=files)
	
	print(f"Upload response: {response.status_code}")
	print(response.json())

def test_request_audio(save_as="received_audio.wav"):
	"""Request audio file from server"""
	response = requests.get(f"{SERVER_URL}/api/audio2")
	
	if response.status_code == 200:
		with open(save_as, "wb") as f:
			f.write(response.content)
		print(f"Audio received and saved as {save_as}")
	else:
		print(f"Error: {response.status_code}")
		print(response.json())

def test_log_sensor_data(device_id, light_value, moisture_value):
	"""Send sensor data to server"""
	data = {
		"device_id": device_id,
		"timestamp": datetime.now().replace(microsecond=0).isoformat(),
		"light_value": light_value,
		"moisture_value": moisture_value
	}
	response = requests.post(f"{SERVER_URL}/api/database", json=data)
	
	print(f"Log response: {response.status_code}")
	print(response.json())

def test_fetch_sensor_data(count=1):
	"""Fetch sensor data from server"""
	response = requests.get(f"{SERVER_URL}/api/database2", params={"count": count})
	
	print(f"Fetch response: {response.status_code}")
	print(response.json())

if __name__ == "__main__":
	# Uncomment the test you want to run
	
	# Test 1: Upload audio
	# test_upload_audio("audio/send/English.wav")
	
	# Test 2: Request audio
	# test_request_audio()
	
	# Test 3: Log sensor data
	# test_log_sensor_data("AGRO-001", 320, 690)
	
	# Test 4: Fetch sensor data
	test_fetch_sensor_data()
	# test_fetch_sensor_data(1)
	# test_fetch_sensor_data(2)
	# test_fetch_sensor_data(14)
