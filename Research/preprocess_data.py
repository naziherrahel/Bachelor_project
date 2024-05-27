import cv2
import json
import os

def preprocess_frame(frame, size=(640, 640)):
    # Resize the frame to the required size
    resized_frame = cv2.resize(frame, size)
    return resized_frame

def capture_and_preprocess(video_path, output_dir, size=(640, 640)):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        preprocessed_frame = preprocess_frame(frame, size)
        output_path = os.path.join(output_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(output_path, preprocessed_frame)
        frame_count += 1
    cap.release()

if __name__ == "__main__":
    with open('camera_config.json', 'r') as file:
        config = json.load(file)
    camera_urls = config['camera_urls']
    output_dir = 'data/preprocessed'
    os.makedirs(output_dir, exist_ok=True)
    for url in camera_urls:
        capture_and_preprocess(url, output_dir)
