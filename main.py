from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Path to save the uploaded and processed images
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def blur_background(image_path, blur_strength=15):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not read image.")

    # Apply Gaussian blur to the entire image
    blur_strength = max(1, int(blur_strength // 2) * 2 + 1)  # Ensure it's an odd number
    blurred_image = cv2.GaussianBlur(image, (blur_strength, blur_strength), 0)

    return blurred_image

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file is uploaded
        if 'image' not in request.files:
            return 'No file uploaded', 400

        file = request.files['image']
        if file.filename == '':
            return 'No selected file', 400

        if file:
            # Secure the filename and save the uploaded image
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Get initial blur strength from form
            blur_strength = int(request.form.get('blur_strength', 15))

            # Process the image to blur the background
            blurred_image = blur_background(file_path, blur_strength)

            # Save the blurred image
            blurred_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"blurred_{filename}")
            cv2.imwrite(blurred_image_path, blurred_image)

            return render_template('index.html', original_image=file_path, blurred_image=blurred_image_path, blur_strength=blur_strength)

    return render_template('index.html')

@app.route('/update_blur', methods=['POST'])
def update_blur():
    data = request.json
    blur_strength = int(data.get('blur_strength', 15))
    print(f"Blur strength requested: {blur_strength}")

    # Reapply blur on the last uploaded image
    original_image = os.path.join(app.config['UPLOAD_FOLDER'], 'your_last_uploaded_image.jpg')  # Change this as needed

    if os.path.exists(original_image):
        try:
            blurred_image = blur_background(original_image, blur_strength)
            blurred_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"blurred_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            cv2.imwrite(blurred_image_path, blurred_image)
            print(f"Blurred image saved at: {blurred_image_path}")
            return jsonify({'success': True, 'blurred_image': blurred_image_path})
        except Exception as e:
            print(f"Error during image processing: {e}")
            return jsonify({'success': False, 'error': str(e)})
    else:
        print("Original image not found.")
        return jsonify({'success': False, 'error': 'Original image not found'})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
