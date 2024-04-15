from flask import Flask, request, send_file, jsonify
import torch
from TTS.api import TTS
import os
import uuid
import whisper

# List available 🐸TTS models
# tts_manager = TTS().list_models()
# all_models = tts_manager.list_models()
# print(f"Models: {all_models}")

# Initialize the Flask application
app = Flask(__name__)

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize the TTS model
api = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC").to(device)

# Whisper
model_name = "base"
device = device
# compute_type = "float32"
model = whisper.load_model(model_name, device=device)

# Ensure the audio directory exists
os.makedirs("audio", exist_ok=True)

@app.route("/synthesize", methods=["POST"])
def synthesize():
    try:
        # Get text from the POST request
        data = request.json
        text = data["text"]

        # Generate a unique filename for the output
        unique_id = uuid.uuid4()
        file_path = f"audio/{unique_id}.wav"

        # Generate the speech file
        api.tts_to_file(text, file_path=file_path)

        # Return the generated speech file
        return send_file(
            file_path, as_attachment=True, attachment_filename=f"{unique_id}.wav"
        )
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Ensure the upload directory exists
        os.makedirs("uploads", exist_ok=True)
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        # Transcribe the audio file using Whisper
        result = model.transcribe(filepath, language='english')

        # Optionally, delete the file after processing if not needed
        os.remove(filepath)

        return (
            jsonify(
                {
                    "message": "File uploaded and transcribed successfully",
                    "transcription": result["text"],
                }
            ),
            200,
        )

    return jsonify({"error": "File upload failed"}), 500

# @app.route("/transcribe", methods=["POST"])
# def transcribe($AUDIO_INPUT):
#     try:
#         result = model.transcribe($AUDIO_INPUT, language='english')
#         print(f' The text in audio: \n {result["text"]}')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
