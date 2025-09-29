from flask import Flask, request, jsonify, render_template_string
import requests
import logging

app = Flask(__name__)

# ESP32 endpoint IP address (replace with your actual ESP32 IP)
ESP32_URL = "http://192.168.4.10/play"

# Configure logging
logging.basicConfig(level=logging.INFO)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Language Player</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background: #222;
        }
        h1 {
            color: #fff;
            margin-bottom: 40px;
            font-size: 2.5em;
        }
        .btn {
            width: 220px;
            padding: 25px;
            margin: 15px;
            font-size: 1.5em;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            color: #fff;
            transition: background 0.2s;
        }
        .hausa { background: #e67e22; }
        .hausa:hover { background: #ca6f1e; }
        .english { background: #2980b9; }
        .english:hover { background: #21618c; }
        .swahili { background: #27ae60; }
        .swahili:hover { background: #1e8449; }
    </style>
</head>
<body>
    <h1>Choose a Language</h1>
    <button class="btn hausa" onclick="play('ha')">Hausa</button>
    <button class="btn english" onclick="play('en')">English</button>
    <button class="btn swahili" onclick="play('sw')">Swahili</button>
    <script>
        function play(lang) {
            fetch(`/play?lang=${lang}`)
                .then(response => response.json())
                .then(data => {
                    alert(`Sent: ${data.lang}`);
                });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/play")
def play():
    lang = request.args.get("lang")
    if lang not in ["ha", "en", "sw"]:
        return jsonify({"error": "Invalid language"}), 400
    logging.info(f"Button pressed: {lang}")
    # Send JSON payload to ESP32 endpoint
    try:
        resp = requests.post(ESP32_URL, json={"lang": lang}, timeout=2)
        logging.info(f"ESP32 response: {resp.status_code}")
    except Exception as e:
        logging.error(f"Error sending to ESP32: {e}")
    return jsonify({"lang": lang})

if __name__ == "__main__":
    # Run Flask on 0.0.0.0:5000 to be accessible over LAN
    app.run(host="0.0.0.0", port=5000, debug=True)
