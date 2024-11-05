# app.py
from flask import Flask, render_template, request, jsonify
from together import Together
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get API key from environment variable
API_KEY = os.getenv('TOGETHER_API_KEY')

# Initialize Together client with API key
try:
    client = Together(api_key=API_KEY)
except Exception as e:
    print(f"Error initializing Together client: {str(e)}")
    client = None

@app.route('/', methods=['GET'])
def home():
    # Pass API key status to template
    has_api_key = bool(API_KEY)
    return render_template('index.html', has_api_key=has_api_key)

@app.route('/generate', methods=['POST'])
def generate_image():
    if not API_KEY:
        return jsonify({'error': 'Together API key not configured. Please set TOGETHER_API_KEY environment variable.'}), 500

    try:
        prompt = request.form.get('prompt')
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        response = client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            width=1024,
            height=768,
            steps=1,
            n=1,
            response_format="b64_json"
        )

        # Get the base64 image data
        image_data = response.data[0].b64_json
        return jsonify({'image': image_data})
    except Exception as e:
        return jsonify({'error': f"Error generating image: {str(e)}"}), 500

if __name__ == '__main__':
    if not API_KEY:
        print("Warning: TOGETHER_API_KEY environment variable not set!")
    app.run(debug=True)