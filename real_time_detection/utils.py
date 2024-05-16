import numpy as np
import cv2
import pyaudio
import wave

def is_moving(track, movement_threshold=5, history_length=3):
    """Check for significant movement over the available frames."""
    num_frames = min(len(track), history_length)
    if num_frames < 2:
        return False  # Not enough data to determine movement.

    total_distance = 0
    for i in range(1, num_frames):
        _, x_prev, y_prev = track[i - 1]
        _, x_curr, y_curr = track[i]
        total_distance += np.sqrt((x_curr - x_prev) ** 2 + (y_curr - y_prev) ** 2)

    avg_distance = total_distance / (num_frames - 1)
    return avg_distance > movement_threshold


def is_dust_cloud(size_changes, track):
    """Determine if an object is a moving dust cloud based on size increase and movement."""
    if len(size_changes) >= 3 and len(track) >= 3:
        size_increasing = size_changes[-1] > size_changes[-3]  # Check size increase over last few frames
        return is_moving(track) and size_increasing
    return False




def is_visibility_obscured(frame, blur_threshold=100.0):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Compute the Laplacian of the image and then the variance
    variance_of_laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()

    # If the variance is below a threshold, the image is considered blurry
    return variance_of_laplacian < blur_threshold




def play_sound(file_path):
    # Open the sound file
    with wave.open(file_path, 'rb') as wf:
        p = pyaudio.PyAudio()

        # Open a stream to play the audio
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Read and play data in chunks
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        # Close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()