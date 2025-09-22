import os
import subprocess

def extract_frames_ffmpeg(video_path, output_dir, fps=30):
    os.makedirs(output_dir, exist_ok=True)
    command = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={fps}",
        os.path.join(output_dir, "frame_%05d.jpg")
    ]
    subprocess.run(command, check=True)
    
import os
import shutil

def save_video_file(file, task_id):
    folder = os.path.join("uploads", task_id)
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file_path

