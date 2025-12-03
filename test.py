import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# 1. Test /api/audio (POST)
def test_post_audio():
    url = f"{BASE_URL}/api/audio"
    audio_path = "audio\send\English.wav"  # Change to a valid audio file path
    files = {"audio": open(audio_path, "rb")}
    response = requests.post(url, files=files)
    print("/api/audio POST response:", response.json())

# 2. Test /api/audio2 (GET)
def test_get_audio2():
    url = f"{BASE_URL}/api/audio2"
    response = requests.get(url)
    if response.status_code == 200:
        with open("received_English.wav", "wb") as f:
            f.write(response.content)
        print("/api/audio2 GET response: Audio file saved as received_English.wav")
    else:
        print("/api/audio2 GET error:", response.json())

# 3. Test /api/database (POST)
def test_post_database():
    url = f"{BASE_URL}/api/database"
    data = {
        "device_id": "AGRO-001",
        "timestamp": "2025-12-01T18:25:43",
        "light_value": 320,
        "moisture_value": 690
    }
    response = requests.post(url, json=data)
    print("/api/database POST response:", response.json())

if __name__ == "__main__":
    # Uncomment the function you want to test
    # test_post_audio()
    # test_get_audio2()
    test_post_database()
