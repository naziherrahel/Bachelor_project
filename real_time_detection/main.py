from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import logging
import json
import asyncio
from inference import process_camera_stream
from websocket_utils import add_websocket, remove_websocket
from fastapi.responses import HTMLResponse

# app = FastAPI()
# security = HTTPBasic()

# # Load camera URLs from JSON configuration
# with open('real_time_detection/camera_config.json', 'r') as file:
#     config = json.load(file)
# camera_urls = config['camera_urls']

# # Base directory
# base_dir = 'c:/Users/Администратор/Desktop/dust_detection_project/'

# logging.basicConfig(level=logging.INFO)

# class StreamRequest(BaseModel):
#     url: str

# def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
#     correct_username = "admin"
#     correct_password = "admin"
#     if credentials.username == correct_username and credentials.password == correct_password:
#         return credentials.username
#     else:
#         raise HTTPException(status_code=401, detail="Incorrect username or password")

# async def run_camera_stream(video_url, stream_id):
#     await asyncio.to_thread(process_camera_stream, video_url, stream_id)

# @app.post("/process_stream")
# async def process_stream(request: StreamRequest, username: str = Depends(get_current_username)):
#     video_url = request.url
#     if video_url not in camera_urls:
#         raise HTTPException(status_code=404, detail="Camera URL not found")
    
#     stream_id = camera_urls.index(video_url) + 1  # Unique stream ID for each video
#     asyncio.create_task(run_camera_stream(video_url, stream_id))
#     return {"message": f"Video stream processing started for stream {stream_id}"}

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket, stream: int):
#     await websocket.accept()
#     add_websocket(stream, websocket)
#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         remove_websocket(stream, websocket)

# @app.get("/")
# def get():
#     with open('real_time_detection/index.html', 'r') as file:
#         return HTMLResponse(content=file.read(), media_type="text/html")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)
from fastapi import FastAPI
from pydantic import BaseModel
import threading
import logging
import json
from inference import process_camera_stream
from websocket_utils import add_websocket, remove_websocket, send_frame_to_websockets
from fastapi.responses import HTMLResponse

app = FastAPI()

# Load camera URLs from JSON configuration
with open('real_time_detection/camera_config.json', 'r') as file:
    config = json.load(file)
camera_urls = config['camera_urls']

# Base directory
base_dir = 'c:/Users/Администратор/Desktop/dust_detection_project/'

logging.basicConfig(level=logging.INFO)

class StreamRequest(BaseModel):
    url: str

@app.post("/process_stream")
def process_stream(request: StreamRequest):
    video_url = request.url
    if video_url not in camera_urls:
        raise HTTPException(status_code=404, detail="Camera URL not found")
    
    stream_id = camera_urls.index(video_url) + 1  # Unique stream ID for each video
    thread = threading.Thread(target=process_camera_stream, args=(video_url, stream_id))
    thread.start()
    return {"message": f"Video stream processing started for stream {stream_id}"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, stream: int):
    await websocket.accept()
    add_websocket(stream, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        remove_websocket(stream, websocket)

@app.get("/")
def get():
    with open('real_time_detection/index.html', 'r') as file:
        return HTMLResponse(content=file.read(), media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
