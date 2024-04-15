from flask import Flask, request, send_file
import torch
from TTS.api import TTS

# Initialize the Flask application
app = Flask(__name__)

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize the TTS model
api = TTS(model_name="tts_models/eng/fairseq/vits").to(device)

@app.route("/synthesize", methods=["POST"])
def synthesize():
    try:
        # Get text from the POST request
        data = request.json
        text = data["text"]

        # Define the output file path
        file_path = "output.wav"

        # Generate the speech file
        api.tts_to_file(text, file_path=file_path)

        # Return the generated speech file
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
