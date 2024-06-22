from collections import defaultdict
import cv2
from ultralytics import YOLO
import logging
import json
import os
from datetime import datetime, timedelta
from utils import is_dust_cloud, play_sound
import asyncio

base_dir = 'c:/Users/Администратор/Desktop/dust_detection_project/'
saved_frames_dir = os.path.join(base_dir, "saved_frames")
sound_file_path = os.path.join(base_dir, "sound_alert.wav")

logging.basicConfig(level=logging.INFO)

# Shared state to debounce audio alerts
last_audio_alert_time = datetime.min
audio_alert_debounce_interval = timedelta(seconds=5)

def process_camera_stream(video_path, stream_id):
    global last_audio_alert_time
    model = YOLO("models/best.pt")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"Error: Could not open video stream {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(f'output_{os.path.basename(video_path)}.avi', fourcc, fps, (frame_width, frame_height))
    if not out.isOpened():
        logging.error("Error: Video writer not opened")
        return

    track_history = defaultdict(lambda: [])
    bbox_size_history = defaultdict(lambda: [])
    frame_count = 0

    try:
        success, ref_frame = cap.read()
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
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
                if is_dust_cloud(bbox_size_history[track_id], track):
                    dust_cloud_detected = True
                    cv2.putText(annotated_frame, f"Dust Cloud ID: {track_id}", (top_left_x, top_left_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.rectangle(annotated_frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 2)
                    frame_timestamp = datetime.now()
                    frame_file_path = os.path.join(saved_frames_dir, f"frame_{frame_count}.jpg")
                    cv2.imwrite(frame_file_path, annotated_frame)
                    if os.path.exists(frame_file_path):
                        logging.info(f"Frame saved: {frame_file_path}")
                    else:
                        logging.error(f"Failed to save frame: {frame_file_path}")

                    from database import insert_frame, insert_detection
                    frame_id = insert_frame(frame_file_path.replace("\\", "/"))
                    insert_detection(timestamp=frame_timestamp, camera_id='camera_1', frame_id=frame_id)

                    if datetime.now() - last_audio_alert_time > audio_alert_debounce_interval:
                        last_audio_alert_time = datetime.now()
                        from websocket_utils import send_audio_alert_to_websockets
                        asyncio.run(send_audio_alert_to_websockets(sound_file_path, stream_id))

            # Always send the current frame to the UI
            from websocket_utils import send_frame_to_websockets
            asyncio.run(send_frame_to_websockets(frame, stream_id, dust_cloud_detected, annotated_frame if dust_cloud_detected else None))

            out.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        logging.error(f"Error occurred during video processing for {video_path}: {e}")
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        logging.info(f"Video processing completed for {video_path}")
