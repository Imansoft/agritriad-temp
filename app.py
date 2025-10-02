# app.py
from flask import Flask, request, jsonify, render_template_string, send_file, abort
from flask_cors import CORS
from pathlib import Path
import logging
import wave

app = Flask(__name__)
CORS(app)

# ---------------- CONFIG ----------------
PROJECT_ROOT = Path(__file__).parent.resolve()
AUDIO_DIR = (PROJECT_ROOT / "audio").resolve()  # e.g. C:\Users\hp\...\AgriTriad\audio
AUDIO_MAP = {
    "en": "English.wav",
    "ha": "Hausa.wav",
    "sw": "Swahili.wav",
}
VALID_LANGS = set(AUDIO_MAP.keys())

# runtime state
selected_lang = None

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agritiad")

# simple UI (optional)
HTML_PAGE = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Agritriad Player</title>
    <style>
        body {
            background: linear-gradient(135deg, #222 60%, #444 100%);
            color: #fff;
            font-family: 'Segoe UI', Arial, sans-serif;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 40px;
            letter-spacing: 2px;
            text-shadow: 0 2px 8px #0008;
        }
        .btn {
            display: block;
            width: 240px;
            padding: 22px 0;
            margin: 18px auto;
            font-size: 1.4em;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            color: #fff;
            box-shadow: 0 2px 12px #0005;
            transition: background 0.2s, transform 0.15s;
        }
        .btn-hausa { background: #e67e22; }
        .btn-hausa:hover { background: #ca6f1e; transform: scale(1.04); }
        .btn-english { background: #2980b9; }
        .btn-english:hover { background: #21618c; transform: scale(1.04); }
        .btn-swahili { background: #27ae60; }
        .btn-swahili:hover { background: #1e8449; transform: scale(1.04); }
        .desc {
            margin-top: 40px;
            font-size: 1.1em;
            color: #bbb;
        }
        code {
            background: #333;
            color: #e67e22;
            padding: 2px 6px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>AgriTriad - Choose Language</h1>
    <button class="btn btn-hausa" onclick="fetch('/play?lang=ha').then(r=>r.json()).then(console.log)">Hausa</button>
    <button class="btn btn-english" onclick="fetch('/play?lang=en').then(r=>r.json()).then(console.log)">English</button>
    <button class="btn btn-swahili" onclick="fetch('/play?lang=sw').then(r=>r.json()).then(console.log)">Swahili</button>
    <div class="desc">ESP32 polls <code>/api/lang</code> for new commands.</div>
</body>
</html>
"""

# ---------------- helpers ----------------
def audio_file_for_lang(lang: str) -> Path:
    if lang not in AUDIO_MAP:
        raise KeyError(lang)
    return (AUDIO_DIR / AUDIO_MAP[lang]).resolve()

def inspect_wav(path: Path):
    """Return (is_pcm:bool, bits:int, sr:int) or raise wave.Error"""
    with wave.open(str(path), 'rb') as wf:
        sampwidth = wf.getsampwidth()
        sr = wf.getframerate()
        comp = wf.getcomptype()
        return (comp == 'NONE'), sampwidth * 8, sr

# ---------------- routes ----------------
@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/lang", methods=["GET"])
def api_lang():
    """
    ESP32 polls this endpoint.
    Response: {"cmd": "en" | "ha" | "sw" | None, "audio_url": "http://host:5000/audio/en" | None}
    """
    global selected_lang
    if selected_lang in VALID_LANGS:
        # build absolute URL for audio (so ESP32 can GET it)
        audio_url = request.url_root.rstrip("/") + f"/audio/{selected_lang}"
        return jsonify({"cmd": selected_lang, "audio_url": audio_url}), 200
    return jsonify({"cmd": None, "audio_url": None}), 200

@app.route("/play")
def play():
    """Browser UI hits this to set the language. We inspect file and log warnings."""
    global selected_lang
    lang = request.args.get("lang", type=str)
    if not lang or lang not in VALID_LANGS:
        return jsonify({"error": "Invalid language"}), 400

    fpath = audio_file_for_lang(lang)
    if not fpath.exists():
        logger.error("Audio file missing for %s: %s", lang, fpath)
    else:
        try:
            is_pcm, bits, sr = inspect_wav(fpath)
            logger.info("Audio %s -> PCM:%s bits:%d sr:%d", fpath.name, is_pcm, bits, sr)
            if not is_pcm:
                logger.warning("Audio is NOT PCM WAV. ESP32 may need decoding.")
            if bits not in (8, 16):
                logger.warning("Unusual bit depth: %d", bits)
        except wave.Error as e:
            logger.exception("Failed reading WAV header: %s", e)

    selected_lang = lang
    logger.info("Selected language: %s (file: %s)", lang, AUDIO_MAP[lang])
    return jsonify({"lang": lang}), 200

@app.route("/audio/<lang>")
def audio(lang):
    """Serve WAV file bytes. 404 if missing."""
    if lang not in VALID_LANGS:
        abort(404)
    fpath = audio_file_for_lang(lang)
    if not fpath.exists():
        logger.error("Requested audio not found: %s", fpath)
        abort(404)
    # stream file
    return send_file(str(fpath), mimetype="audio/wav", as_attachment=False)

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

# -------------- startup --------------
if __name__ == "__main__":
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Project root: %s", PROJECT_ROOT)
    logger.info("Audio dir: %s", AUDIO_DIR)
    logger.info("Expecting filenames: %s", AUDIO_MAP)
    app.run(host="0.0.0.0", port=5000, debug=True)
