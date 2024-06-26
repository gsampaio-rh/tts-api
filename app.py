from flask import Flask, request, send_file, jsonify, make_response
from flask_cors import CORS
import torch
from TTS.api import TTS
import os
import uuid
import whisper
import logging

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s - %(levelname)s - %(message)s",
)

# List available 🐸TTS models
# tts_manager = TTS().list_models()
# all_models = tts_manager.list_models()
# print(f"Models: {all_models}")

# Initialize the Flask application
app = Flask(__name__)

# This setup allows for more fine-grained control over CORS headers.
CORS(
    app,
    resources={
        r"/synthesize": {
            "origins": "*",  # Be cautious with using '*', specify domains in production
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        }
    },
)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["AUDIO_FOLDER"] = "audio"

# Additional logging setup if you want to log to console as well
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"Using device: {device}")

# Initialize the TTS model
api = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC").to(device)

# Whisper
model_name = "base"
model = whisper.load_model(model_name, device=device)

# Ensure the audio directory exists
# os.makedirs("audio", exist_ok=True)

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route("/synthesize", methods=["POST", "OPTIONS"])
def synthesize():
    if request.method == "OPTIONS":
        # This is to ensure that Flask-CORS handles OPTIONS requests properly.
        return _build_cors_preflight_response()
    elif request.method == "POST":
        try:
            data = request.json
            text = data.get("text", "")
            logging.info(f"Received synthesis request: {text}")

            unique_id = uuid.uuid4()
            file_name = f"{unique_id}.wav"
            # Use these paths in your route
            filepath = os.path.join(app.config["AUDIO_FOLDER"], file_name)

            api.tts_to_file(text, file_path=filepath)
            logging.info(f"Generated speech file saved to {filepath}")

            return send_file(filepath, as_attachment=True, download_name=f"{unique_id}.wav")
        except Exception as e:
            logging.error(f"Error in synthesis: {str(e)}", exc_info=True)
            return {"error": str(e)}, 500
        pass

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "audio" not in request.files:
        logging.warning("No audio file part in request")
        return jsonify({"error": "No file part"}), 400

    file = request.files["audio"]
    if file.filename == "":
        logging.warning("Received file with no filename")
        return jsonify({"error": "No selected file"}), 400

    try:
        os.makedirs("uploads", exist_ok=True)
        # Use these paths in your route
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        logging.info(f"File uploaded to {filepath}")

        result = model.transcribe(filepath)
        logging.info(f"Transcription successful: {result['text']}")

        # os.remove(filepath)
        # logging.info(f"File deleted after processing: {filepath}")

        return (
            jsonify(
                {
                    "message": "File uploaded and transcribed successfully",
                    "transcription": result["text"],
                }
            ),
            200,
        )
    except Exception as e:
        logging.error(f"Error in transcription: {str(e)}", exc_info=True)
        return jsonify({"error": "File upload failed"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
