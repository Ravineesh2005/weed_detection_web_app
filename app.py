from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
import os
import cv2
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
        try:
            model_cache[model_name] = YOLO(model_path)
        except Exception as e:
            return jsonify({'error': f'Failed to load model: {str(e)}'}), 500
            
    model = model_cache[model_name]
    
    file = request.files['image']
    temp_path = f'temp_{uuid.uuid4().hex}.jpg'
    file.save(temp_path)
    
    results = model.predict(source=temp_path, conf=0.5)
    
    detections = []
    im_b64 = ""
    for r in results:
        for box in r.boxes:
            detections.append({
                'confidence': float(box.conf[0]),
                'bbox': box.xyxy[0].tolist()
            })
        
        # Generate annotated image (BGR to base64 jpg)
        im_bgr = r.plot()
        _, im_arr = cv2.imencode('.jpg', im_bgr)
        im_b64 = base64.b64encode(im_arr.tobytes()).decode('utf-8')
    
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