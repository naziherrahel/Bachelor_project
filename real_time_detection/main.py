from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import json
import asyncio
from inference import process_camera_stream
from websocket_utils import add_websocket, remove_websocket
from fastapi.responses import HTMLResponse
from database import get_all_frames, get_camera_info, get_detailed_detections
import os

app = FastAPI()
security = HTTPBasic()

# Load camera URLs from JSON configuration
with open('real_time_detection/camera_config.json', 'r') as file:
    config = json.load(file)
camera_urls = config['camera_urls']

# Base directory
base_dir = 'c:/Users/Администратор/Desktop/dust_detection_project/'
saved_frames_dir = os.path.join(base_dir, "saved_frames")

logging.basicConfig(level=logging.INFO)

class StreamRequest(BaseModel):
    url: str

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "admin"
    correct_password = "admin"
    if credentials.username == correct_username and credentials.password == correct_password:
        return credentials.username
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

async def run_camera_stream(video_url, stream_id):
    await asyncio.to_thread(process_camera_stream, video_url, stream_id)

@app.post("/process_stream")
async def process_stream(request: StreamRequest, username: str = Depends(get_current_username)):
    video_url = request.url
    if video_url not in camera_urls:
        camera_urls.append(video_url)
        with open('real_time_detection/camera_config.json', 'w') as file:
            json.dump({'camera_urls': camera_urls}, file)
    stream_id = camera_urls.index(video_url) + 1  # Unique stream ID for each video
    asyncio.create_task(run_camera_stream(video_url, stream_id))
    return {"message": f"Video stream processing started for stream {stream_id}"}

async def websocket_auth(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        credentials = HTTPBasicCredentials(username=data["username"], password=data["password"])
        get_current_username(credentials)
    except Exception as e:
        await websocket.close(code=1008)
        logging.error(f"WebSocket connection rejected: {e}")
        return False
    return True

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, stream: int):
    logging.info(f"New WebSocket connection attempt on stream {stream}")
    if not await websocket_auth(websocket):
        return
    add_websocket(stream, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            logging.info(f"Received message on stream {stream}: {message}")
    except WebSocketDisconnect:
        logging.info(f"WebSocket disconnected on stream {stream}")
        remove_websocket(stream, websocket)

@app.get("/")
def get():
    with open('real_time_detection/index.html', 'r') as file:
        return HTMLResponse(content=file.read(), media_type="text/html")

@app.get("/camera_info_page")
async def camera_info_page(username: str = Depends(get_current_username)):
    with open('real_time_detection/camera_info.html', 'r') as file:
        return HTMLResponse(content=file.read(), media_type="text/html")

@app.get("/saved_frames_page")
async def saved_frames_page(username: str = Depends(get_current_username)):
    with open('real_time_detection/saved_frames.html', 'r') as file:
        return HTMLResponse(content=file.read(), media_type="text/html")

@app.get("/camera_info")
async def camera_info(username: str = Depends(get_current_username)):
    try:
        info = get_detailed_detections()
        return {"camera_info": info}
    except Exception as e:
        logging.error(f"Error fetching camera info: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/saved_frames")
async def saved_frames(username: str = Depends(get_current_username)):
    try:
        frames = get_all_frames()
        logging.info(f"Frames fetched: {frames}")
        valid_frames = []
        for frame in frames:
            file_path = os.path.join(saved_frames_dir, os.path.basename(frame['url']))
            if os.path.exists(file_path):
                valid_frames.append({"url": f"/frames/{os.path.basename(frame['url'])}"})
            else:
                logging.warning(f"File not found: {file_path}")
        logging.info(f"Valid Frame URLs: {valid_frames}")
        return {"frames": valid_frames}
    except Exception as e:
        logging.error(f"Error fetching saved frames: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Conditionally mount the frames directory
if os.path.exists(saved_frames_dir) and any(os.scandir(saved_frames_dir)):
    app.mount("/frames", StaticFiles(directory=saved_frames_dir), name="frames")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
