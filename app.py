from flask import Flask, request, jsonify
from ultralytics import YOLO
import os

app = Flask(__name__)
model = YOLO('best.pt')

@app.route('/')
def home():
    return 'YOLO Weed Detection API Ready!'

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image'}), 400
    
    file = request.files['image']
    temp_path = 'temp.jpg'
    file.save(temp_path)
    
    results = model.predict(source=temp_path, conf=0.5)
    
    detections = []
    for r in results:
        for box in r.boxes:
            detections.append({
                'confidence': float(box.conf[0]),
                'bbox': box.xyxy[0].tolist()
            })
    
    os.remove(temp_path)
    return jsonify({
        'detections': detections,
        'count': len(detections),
        'success': True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)