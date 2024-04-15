from flask import Flask, request, send_file
import torch
from TTS.api import TTS
import os
import uuid

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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
