import os
import shutil

def save_video_file(file, task_id):
    folder = os.path.join("uploads", task_id)
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file_path
