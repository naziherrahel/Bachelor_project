import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load database configuration
with open('C:/Users/Администратор/Desktop/dust_detection_project/database_setup/db_config.json', 'r') as file:
    config = json.load(file)

def setup_database():
    conn = None
    cursor = None
    try:
        # Connect to default database to create the new database
        conn = psycopg2.connect(
            dbname="postgres",
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Create the 'dust_detection' database
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'dust_detection'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("CREATE DATABASE dust_detection")
            print("Database created successfully")
        else:
            print("Database 'dust_detection' already exists")    
        
        # Close cursor and connection to default database
        cursor.close()
        conn.close()

        # Connect to the new 'dust_detection' database
        conn = psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        cursor = conn.cursor()

       # Create 'frames' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS frames (
                frame_id SERIAL PRIMARY KEY,
                file_path VARCHAR(255) NOT NULL
            );
        """)
        conn.commit()  # Explicit commit after table creation
        print("Frames table created successfully")

        # Create 'detections' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                detection_id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                camera_id VARCHAR(255) NOT NULL,
                frame_id INT REFERENCES frames (frame_id)
            );
        """)
        conn.commit()  # Explicit commit after table creation
        print("Detections table created successfully")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:    
        # Close cursor and connection
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    setup_database()
