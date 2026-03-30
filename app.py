from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
import os
import cv2
import base64
app = Flask(__name__)
model = YOLO('models/best.pt')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image'}), 400
    
    file = request.files['image']
    temp_path = 'temp.jpg'
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