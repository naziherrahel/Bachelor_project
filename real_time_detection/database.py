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

def get_all_frames():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM frames")
    frames = cursor.fetchall()
    conn.close()
    return [{"url": frame[0]} for frame in frames]

def get_camera_info():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT camera_id, COUNT(*) as detection_count
        FROM detections
        GROUP BY camera_id
    """)
    info = cursor.fetchall()
    conn.close()
    return [{"camera_id": row[0], "detection_count": row[1]} for row in info]

def get_detailed_detections():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.timestamp, d.camera_id, f.file_path
        FROM detections d
        JOIN frames f ON d.frame_id = f.frame_id
        ORDER BY d.timestamp DESC
    """)
    detections = cursor.fetchall()
    conn.close()
    return [{"timestamp": row[0], "camera_id": row[1], "file_path": row[2]} for row in detections]
