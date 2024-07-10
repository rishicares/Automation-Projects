import cv2
import numpy as np
import yaml
from yaml.loader import SafeLoader

# Load the YOLO configuration from a YAML file
with open(r'C:\\Users\\rishi\\OneDrive - Storage\\Programming\\Automation-Projects\\yolo\\data.yaml', mode='r') as f:
    daya_yaml = yaml.load(f, Loader=SafeLoader)
labels = daya_yaml['names']

# Load the YOLO model from an ONNX file
yolo = cv2.dnn.readNetFromONNX(r'C:\\Users\\rishi\\OneDrive - Storage\\Programming\\Automation-Projects\\yolo\\Model\\weights\\best.onnx')

# Set backend and target to be used by YOLO
yolo.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
yolo.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Precaptured video path
video_path = r"C:\\Users\\rishi\\Downloads\\video1.mp4"
cap = cv2.VideoCapture(video_path)

# Uncomment the line below to use webcam instead
# cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()  # Read frame from video

    if not ret:  # If no frame is captured (end of video), break out of loop
        break

    # Preprocess frame and prepare input image for YOLO
    max_rc = max(frame.shape[:2])
    input_image = np.zeros((max_rc, max_rc, 3), dtype=np.uint8)
    input_image[0:frame.shape[0], 0:frame.shape[1]] = frame  # Paste frame into canvas

    # Define input size for YOLO
    INPUT_WH_YOLO = 640
    blob = cv2.dnn.blobFromImage(input_image, 1/255, (INPUT_WH_YOLO, INPUT_WH_YOLO), swapRB=True, crop=False)
    yolo.setInput(blob)
    preds = yolo.forward()

    # Process detections and draw bounding boxes
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
        if confidence > 0.4:  # Filter detections by confidence threshold
            class_score = row[5:].max()
            class_id = row[5:].argmax()
            if class_score > 0.25:  # Filter detections by class score threshold
                # Get bounding box coordinates
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

    # Apply Non-Maxima Suppression to filter overlapping boxes
    output = cv2.dnn.NMSBoxes(boxes_np, confidences_np, 0.25, 0.45)

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

        # Draw bounding box and label on the frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 0), 1)

    # Display frame with bounding boxes
    cv2.imshow('YOLO Object Detection', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

