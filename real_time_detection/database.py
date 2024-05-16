import psycopg2
import json

# Load database configuration
with open('C:/Users/Администратор/Desktop/dust_detection_project/database_setup/db_config.json', 'r') as file:
    config = json.load(file)

def connect_db():
    return psycopg2.connect(
        dbname=config['dbname'],
        user=config['user'],
        password=config['password'],
        host=config['host'],
        port=config['port']
    )

def insert_detection(timestamp, camera_id, frame_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO detections (timestamp, camera_id, frame_id) VALUES (%s, %s, %s)",
                   (timestamp, camera_id, frame_id))
    conn.commit()
    cursor.close()
    conn.close()

def insert_frame(file_path):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO frames (file_path) VALUES (%s) RETURNING frame_id", (file_path,))
    frame_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return frame_id
