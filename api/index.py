from flask import Flask, render_template, request, jsonify
from together import Together
import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
from urllib.parse import urlparse

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

# # Database configuration
# tmpPostgres = urlparse(os.getenv("DATABASE_URL"))
# DATABASE_URL = f"postgresql+asyncpg://{tmpPostgres.username}:{tmpPostgres.password}@{tmpPostgres.hostname}{tmpPostgres.path}?ssl=require"

# async def store_email(email):
#     engine = create_async_engine(DATABASE_URL, echo=True)
#     async with engine.begin() as conn:  # Start transaction with engine.begin()
#         await conn.execute(text("INSERT INTO emails (email) VALUES (:email)"), {"email": email})
#     await engine.dispose()

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

# @app.route('/store-email', methods=['POST'])
# async def store_email_route():
#     data = request.get_json()
#     email = data.get('email')

#     if not email:
#         return jsonify({"message": "Email is required!"}), 400

#     try:
#         await store_email(email)
#         return jsonify({"message": "Email stored successfully!"}), 200
#     except Exception as e:
#         return jsonify({"message": f"Failed to store email: {str(e)}"}), 500

if __name__ == '__main__':
    if not API_KEY:
        print("Warning: TOGETHER_API_KEY environment variable not set!")
    app.run(debug=True)
