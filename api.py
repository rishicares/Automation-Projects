import cv2
import numpy as np
import yaml
from yaml.loader import SafeLoader
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import io
import tempfile
import os

app = FastAPI()

@app.post("/detect_video/")
async def detect_objects_video(file: UploadFile = File(..., upload_file_size=10 * 1024 * 1024)):

    # Load YAML file containing class labels
    with open(r'C:\\Users\\rishi\\OneDrive - Storage\\Programming\\Automation-Projects\\yolo\\data.yaml', mode='r') as f:
        data_yaml = yaml.load(f, Loader=SafeLoader)
    labels = data_yaml['names']

    # Load YOLO model from ONNX format
    yolo = cv2.dnn.readNetFromONNX(r'C:\\Users\\rishi\\OneDrive - Storage\\Programming\\Automation-Projects\\yolo\\Model\\weights\\best.onnx')
    yolo.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    yolo.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def process_frame(frame):
        max_rc = max(frame.shape[:2])
        input_image = np.zeros((max_rc, max_rc, 3), dtype=np.uint8)
        input_image[0:frame.shape[0], 0:frame.shape[1]] = frame
        INPUT_WH_YOLO = 640
        blob = cv2.dnn.blobFromImage(input_image, 1/255, (INPUT_WH_YOLO, INPUT_WH_YOLO), swapRB=True, crop=False)
        yolo.setInput(blob)
        preds = yolo.forward()

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
                    box = np.array([left, top, width, height])

                    confidences.append(class_score)
                    boxes.append(box)
                    classes.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45)
        
        for i in indices:
            box = boxes[i]
            left, top, width, height = box
            cv2.rectangle(frame, (left, top), (left + width, top + height), (0, 255, 0), 2)
            label = f'{labels[classes[i]]}: {confidences[i]:.2f}'
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

        return frame

    @app.post("/detect_video/")
    async def detect_objects_video(file: UploadFile = File(...)):
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Open the video file
        cap = cv2.VideoCapture(temp_file_path)
        
        if not cap.isOpened():
            os.unlink(temp_file_path)
            raise HTTPException(status_code=400, detail="Unable to open video file")

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Create a video writer object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_path = temp_file_path.replace('.mp4', '_processed.mp4')
        out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame = process_frame(frame)
            out.write(processed_frame)

        # Release resources
        cap.release()
        out.release()
        os.unlink(temp_file_path)

        # Return the processed video
        def iterfile():
            with open(out_path, mode="rb") as file_like:
                yield from file_like

        return StreamingResponse(iterfile(), media_type="video/mp4")

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001)