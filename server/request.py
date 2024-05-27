import requests
import json

# URL of the FastAPI endpoint
url = "http://127.0.0.1:8000/process_stream"

# List of video URLs to process
video_urls = [
    "C:/Users/Администратор/Desktop/dust_detection_project/test_data/videos/2.mp4",
    "C:/Users/Администратор/Desktop/dust_detection_project/test_data/videos/video1.mp4"
]

headers = {
    "Content-Type": "application/json"
}

# Authentication credentials
auth = ("admin", "admin")

# Sending POST requests for each video URL
for video_url in video_urls:
    payload = {
        "url": video_url
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload), auth=auth)
    print(response.json())
