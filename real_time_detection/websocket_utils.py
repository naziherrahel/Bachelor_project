
import cv2
import base64
import asyncio
import json

# Dictionary to hold active websockets for each stream
active_websockets = {}

def add_websocket(stream_id, websocket):
    if stream_id not in active_websockets:
        active_websockets[stream_id] = []
    active_websockets[stream_id].append(websocket)
    print(f"WebSocket added for stream {stream_id}. Total active: {len(active_websockets[stream_id])}")

def remove_websocket(stream_id, websocket):
    if stream_id in active_websockets and websocket in active_websockets[stream_id]:
        active_websockets[stream_id].remove(websocket)
        print(f"WebSocket removed for stream {stream_id}. Total active: {len(active_websockets[stream_id])}")

async def send_frame_to_websockets(frame, stream_id, dust_cloud_detected, annotated_frame):
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    message = json.dumps({"type": "frame", "data": jpg_as_text})
    if stream_id in active_websockets:
        for websocket in active_websockets[stream_id]:
            try:
                await websocket.send_text(message)
                print(f"Frame sent to WebSocket for stream {stream_id}")
            except Exception as e:
                print(f"Error sending frame to websocket for stream {stream_id}: {e}")

    if dust_cloud_detected and annotated_frame is not None:
        _, annotated_buffer = cv2.imencode('.jpg', annotated_frame)
        annotated_jpg_as_text = base64.b64encode(annotated_buffer).decode('utf-8')
        alert_message = json.dumps({"type": "alert", "data": annotated_jpg_as_text})
        if stream_id in active_websockets:
            for websocket in active_websockets[stream_id]:
                try:
                    await websocket.send_text(alert_message)
                    print(f"Alert frame sent to WebSocket for stream {stream_id}")
                except Exception as e:
                    print(f"Error sending alert frame to websocket for stream {stream_id}: {e}")

async def send_audio_alert_to_websockets(audio_path, stream_id):
    with open(audio_path, 'rb') as audio_file:
        audio_data = audio_file.read()
        audio_as_text = base64.b64encode(audio_data).decode('utf-8')
        message = json.dumps({"type": "audio", "data": audio_as_text})
        if stream_id in active_websockets:
            for websocket in active_websockets[stream_id]:
                try:
                    await websocket.send_text(message)
                    print(f"Audio alert sent to WebSocket for stream {stream_id}")
                except Exception as e:
                    print(f"Error sending audio to websocket for stream {stream_id}: {e}")
