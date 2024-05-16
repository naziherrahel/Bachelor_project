from collections import defaultdict
import cv2
# import numpy as np
from ultralytics import YOLO
import threading
import logging
from utils import is_dust_cloud
import json
import os 
from datetime import datetime
from database import insert_detection, insert_frame
from utils import is_dust_cloud, is_visibility_obscured, is_visibility_obscured
from utils import play_sound

################# noise adding for quality testing ##################
import cv2
import numpy as np
import random

def add_noise(frame, noise_level=0.50):
    # Ensure the frame is in BGR format
    img_array = np.asarray(frame)

    # Generate noise
    noise = np.random.randint(0, 256, img_array.shape, dtype=np.uint8)
    noisy_image = img_array.copy()

    # Apply noise based on the specified noise level
    num_noise_pixels = int(noise_level * img_array.size / img_array.shape[-1])
    for _ in range(num_noise_pixels):
        x, y = random.randint(0, img_array.shape[0] - 1), random.randint(0, img_array.shape[1] - 1)
        noisy_image[x, y] = noise[x, y]

    return noisy_image
############################ adding blur to our frames ###################
 

def apply_blur(frame, blur_percentage=0.10):
    # Calculate the kernel size based on the frame dimensions and blur percentage
    # Kernel size needs to be odd, and is proportional to the image size
    height, width = frame.shape[:2]
    kernel_size = int(min(height, width) * blur_percentage)
    kernel_size = kernel_size if kernel_size % 2 != 0 else kernel_size + 1  # Kernel size must be odd

    # Apply Gaussian blur
    if kernel_size > 1:  # Kernel size 1 means no blur
        blurred_frame = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    else:
        blurred_frame = frame

    return blurred_frame

######################################### humidity #######################

def simulate_high_humidity(frame, intensity=0.2):
    # Convert frame to float for precision during manipulation
    frame_float = frame.astype(np.float64)

    # Create a haze layer, which is a white fog-like overlay
    haze = np.full(frame.shape, 255, dtype=np.float64) * intensity
    
    # Blend the haze with the original frame
    foggy_frame = cv2.addWeighted(frame_float, 1 - intensity, haze, intensity, 0)

    # Convert back to uint8
    foggy_frame = np.clip(foggy_frame, 0, 255).astype(np.uint8)

    # Optionally, reduce contrast to enhance the haze effect
    foggy_frame = cv2.addWeighted(foggy_frame, 1 - intensity, foggy_frame, 0, 32 * intensity)

    return foggy_frame



# Defining our base directory of your project
base_dir = 'c:/Users/Администратор/Desktop/dust_detection_project/'

logging.basicConfig(level=logging.INFO)


def process_camera_stream(video_path):
    # Initialize YOLO model inside each thread
    model = YOLO("trained_models/best.pt")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"Error: Could not open video stream {video_path}")
        return

    # Retrieve video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(f'output_{video_path[-5]}.avi', fourcc, fps, (frame_width, frame_height))
    if not out.isOpened():
        logging.error("Error: Video writer not opened")
        return

    # Initialize tracking and size history
    track_history = defaultdict(lambda: [])
    bbox_size_history = defaultdict(lambda: [])
    frame_count = 0

    try:
        success, ref_frame = cap.read()
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # frame = cv2.GaussianBlur(frame, (19, 19), 0)
            # frame = add_noise(frame, noise_level=0.50)
            # Apply blur to the frame
            frame = apply_blur(frame, blur_percentage=0.3)  # Adjust blur percentage as needed
             # Apply high humidity effect to the frame
            # frame = simulate_high_humidity(frame, intensity=0.7)  # Adjust intensity as needed


            
            frame_count += 1
            results = model.track(frame, persist=True)
            boxes = results[0].boxes.xywh.cpu() if results[0].boxes is not None else []
            track_ids = results[0].boxes.id.int().cpu().tolist() if results[0].boxes and results[0].boxes.id is not None else []
            dust_cloud_detected = False
            annotated_frame = frame.copy()

           

            for box, track_id in zip(boxes, track_ids):
                    center_x, center_y, w, h = box
                    top_left_x = int(center_x - w / 2)
                    top_left_y = int(center_y - h / 2)
                    bottom_right_x = int(center_x + w / 2)
                    bottom_right_y = int(center_y + h / 2)

                    bbox_area = w * h
                    bbox_size_history[track_id].append(bbox_area)
                    track = track_history[track_id]
                    track.append((frame_count, center_x, center_y))
                    dust_cloud_detected = True
                    cv2.putText(annotated_frame, f"Dust Cloud ID: {track_id}", (top_left_x, top_left_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.rectangle(annotated_frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 2)
                    # Get the current timestamp
                    frame_timestamp = datetime.now()
                    # Save frame as an image
                    frame_file_path = f"{base_dir}saved_frames/frame_{frame_count}.jpg"
                    cv2.imwrite(frame_file_path, frame)
                    sound_file_path = "C:/Users/Администратор/Desktop/dust_detection_project/sound_alert.wav"  
                    play_sound(sound_file_path)


                    # Insert frame into database and get frame_id
                    # frame_id = insert_frame(frame_file_path)


                    # Insert detection data into database
                    # Note: Replace 'camera_id' with actual camera identifier
                    # insert_detection(timestamp=frame_timestamp, camera_id='camera_1', frame_id=frame_id)

            frame_to_write = annotated_frame if dust_cloud_detected else frame
            out.write(frame_to_write)
            cv2.imshow(f"YOLOv8 Tracking {video_path[-5]}", frame_to_write)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        logging.error(f"Error occurred during video processing for {video_path}: {e}")
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        logging.info(f"Video processing completed for {video_path}")


# List of our camera RTSP URLs

with open('camera_config.json', 'r') as file:
    config = json.load(file)
camera_urls = config['camera_urls']

# Creating threads for each camera
threads = []
for url in camera_urls:
    thread = threading.Thread(target=process_camera_stream, args=(url,))
    threads.append(thread)
    thread.start()

# Join threads to ensure each completes before exiting the script
for thread in threads:
    thread.join()

