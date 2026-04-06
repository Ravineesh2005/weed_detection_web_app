from flask import Flask, request, jsonify, render_template
# from ultralytics import YOLO
import os
# import cv2
import base64
import uuid
app = Flask(__name__)
model_cache = {}

@app.route('/')
def home():
    models_dir = 'models'
    if os.path.exists(models_dir):
        available_models = [f for f in os.listdir(models_dir) if f.endswith('.pt')]
    else:
        available_models = []
    return render_template('index.html', models=available_models)

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image'}), 400
    
    model_name = request.form.get('model_name')
    if not model_name:
        return jsonify({'error': 'No model selected'}), 400
        
    model_path = os.path.join('models', model_name)
    if not os.path.exists(model_path) or not model_path.endswith('.pt'):
        return jsonify({'error': 'Model file not found'}), 404
        
    if model_name not in model_cache:
        model_cache[model_name] = "Dummy Model"
            
    # Mock inference
    file = request.files['image']
    temp_path = f'temp_{uuid.uuid4().hex}.jpg'
    file.save(temp_path)
    
    detections = [
        {'confidence': 0.99, 'bbox': [10, 10, 100, 100]}
    ]
    im_b64 = "MOCK_BASE64_IMAGE_DATA_WOULD_BE_HERE"
    
    try:
        os.remove(temp_path)
    except:
        pass

    return jsonify({
        'detections': detections,
        'count': len(detections),
        'image_base64': im_b64,
        'success': True
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)