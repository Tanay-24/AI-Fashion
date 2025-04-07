from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from google import generativeai as genai
from PIL import Image
from io import BytesIO
import os

# Setup Flask
app = Flask(__name__)
CORS(app)

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Gemini API Key
genai.configure(api_key="AIzaSyBZEgzKt0gYQLjKnZeDW8F9Ixe9AMFRKzY")  # 🔑 Replace with your actual key

# Home route (optional)
@app.route("/", methods=["GET"])
def home():
    return "<h2>Use /predict to POST an image and get styled output</h2>"

# Function to generate image with prompt
def generate_styled_image(image, prompt):
    print(f"[DEBUG] Prompt:\n{prompt}")

    # Convert image to bytes
    img_io = BytesIO()
    image.save(img_io, format='PNG')
    img_io.seek(0)
    image_data = img_io.getvalue()

    # Gemini model call
    model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

    response = model.generate_content([
        prompt,
        {"mime_type": "image/png", "data": image_data}
    ])

    # Extract generated image
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data.data:
            print("[DEBUG] Styled image received.")
            return Image.open(BytesIO(part.inline_data.data))

    raise Exception("No image returned from Gemini.")

# Endpoint: POST /predict
@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['file']
    try:
        image = Image.open(file.stream).convert("RGB")
    except Exception as e:
        return jsonify({"error": f"Invalid image: {e}"}), 400

    # 🔥 HARDCODED PROMPT
    prompt = "Hi, this is a picture of me. Can you add a llama next to me?"

    try:
        styled_image = generate_styled_image(image, prompt)
        output = BytesIO()
        styled_image.save(output, format="JPEG")
        output.seek(0)
        return send_file(output, mimetype='image/jpeg')
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == "__main__":
    print("[INFO] Flask app running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)
