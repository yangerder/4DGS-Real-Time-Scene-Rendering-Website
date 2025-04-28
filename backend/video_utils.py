import os
import subprocess

def extract_frames_ffmpeg(video_path, output_dir, fps=15):
    os.makedirs(output_dir, exist_ok=True)
    command = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={fps}",
        os.path.join(output_dir, "frame_%04d.png")
    ]
    subprocess.run(command, check=True)
