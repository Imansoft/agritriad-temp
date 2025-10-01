from flask import Flask, request, jsonify, render_template_string
import logging

app = Flask(__name__)

selected_lang = None  # Store the last selected language

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
                    alert(`Selected: ${data.lang}`);
                });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

# API endpoint for ESP32 to poll for the latest language selection
@app.route("/api/lang", methods=["GET"])
def api_lang():
    if selected_lang in ["ha", "en", "sw"]:
        return jsonify({"lang": selected_lang})
    else:
        return jsonify({"lang": None}), 200

# Endpoint for the website to set the language
@app.route("/play")
def play():
    global selected_lang
    lang = request.args.get("lang")
    if lang not in ["ha", "en", "sw"]:
        return jsonify({"error": "Invalid language"}), 400
    selected_lang = lang
    logging.info(f"Button pressed: {lang}")
    return jsonify({"lang": lang})

if __name__ == "__main__":
    # Run Flask on 0.0.0.0:5000 to be accessible over LAN
    app.run(host="0.0.0.0", port=5000, debug=True)
