from flask import Flask, request, jsonify
import cv2
import numpy as np
import os
import tempfile
import yaml
from yaml.loader import SafeLoader

app = Flask(__name__)

# Load YAML file containing class labels.
with open(r'C:\\Users\\rishi\\OneDrive - Storage\\Programming\\Automation-Projects\\yolo\\data.yaml', mode='r') as f:
    data_yaml = yaml.load(f, Loader=SafeLoader)
labels = data_yaml['names']

# Load YOLO model from ONNX format.
yolo = cv2.dnn.readNetFromONNX(r'C:\\Users\\rishi\\OneDrive - Storage\\Programming\\Automation-Projects\\yolo\\Model\\weights\\best.onnx')
yolo.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
yolo.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Directory to save processed videos
PROCESSED_VIDEO_DIR = 'processed_videos'
os.makedirs(PROCESSED_VIDEO_DIR, exist_ok=True)

# Function to process the video
def process_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Preprocess frame and perform YOLO object detection.
        max_rc = max(frame.shape[:2])
        input_image = np.zeros((max_rc, max_rc, 3), dtype=np.uint8)
        input_image[0:frame.shape[0], 0:frame.shape[1]] = frame
        INPUT_WH_YOLO = 640
        blob = cv2.dnn.blobFromImage(input_image, 1/255, (INPUT_WH_YOLO, INPUT_WH_YOLO), swapRB=True, crop=False)
        yolo.setInput(blob)
        preds = yolo.forward()

        # Process detections and draw bounding boxes.
        detections = preds[0]
        boxes = []
        confidences = []
        classes = []

        image_w, image_h = input_image.shape[:2]
        x_factor = image_w / INPUT_WH_YOLO
        y_factor = image_h / INPUT_WH_YOLO

        for i in range(len(detections)):
            row = detections[i]
            confidence = row[4]
            if confidence > 0.4:
                class_score = row[5:].max()
                class_id = row[5:].argmax()
                if class_score > 0.25:
                    cx, cy, w, h = row[0:4]
                    left = int((cx - 0.5 * w) * x_factor)
                    top = int((cy - 0.5 * h) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * y_factor)
                    box = np.array([left, top, left + width, top + height])

                    confidences.append(class_score)
                    boxes.append(box)
                    classes.append(class_id)

        boxes_np = np.array(boxes)
        confidences_np = np.array(confidences)
        output = cv2.dnn.NMSBoxes(boxes_np.tolist(), confidences_np.tolist(), 0.25, 0.45)
        if len(output) > 0:
            index = output.flatten()
        else:
            index = np.empty((0,), dtype=int)

        for ind in index:
            x, y, w, h = boxes_np[ind]
            bb_conf = int(confidences_np[ind] * 100)
            class_id = classes[ind]
            class_name = labels[class_id]
            text = f'{class_name}: {bb_conf}%'

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.rectangle(frame, (x, y - 30), (x + w, y), (255, 255, 255), -1)
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 0), 1)

        out.write(frame)

    cap.release()
    out.release()

@app.route('/process_video', methods=['POST'])
def process_video_endpoint():
    if 'video' not in request.files:
        return jsonify(error="No video file provided"), 400

    video_file = request.files['video']

    # Save the uploaded video to a temporary file
    input_path = tempfile.mktemp(suffix='.mp4')
    video_file.save(input_path)

    # Path for the processed video
    output_filename = os.path.join(PROCESSED_VIDEO_DIR, f"processed_{os.path.basename(input_path)}")
    output_path = os.path.abspath(output_filename)

    # Process the video
    process_video(input_path, output_path)

    # Return the path of the processed video
    return jsonify(processed_video_path=output_path)

if __name__ == '__main__':
    app.run(debug=True)