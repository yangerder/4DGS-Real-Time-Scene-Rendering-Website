# routers/multiview.py
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from utils.video_utils import extract_frames_ffmpeg
import os, shutil, subprocess
from typing import List
from pathlib import Path
# 假設這個 routers/multiview.py 路徑為 your_project/routers/multiview.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # your_project/routers
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "4DGaussians"))  # ../4DGaussians


router = APIRouter()

@router.post("/upload_multiview")
async def upload_multiview(files: List[UploadFile] = File(...), dataset_name: str = Form(...)):
    dataset_path = Path(f"{ROOT_DIR}/data/multipleview/{dataset_name}")
    dataset_path.mkdir(parents=True, exist_ok=True)

    for i, file in enumerate(files):
        cam_name = f"cam{str(i+1).zfill(2)}"
        cam_path = dataset_path / cam_name
        cam_path.mkdir(parents=True, exist_ok=True)

        video_path = cam_path / f"video_rgb.mp4"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extract_frames_ffmpeg(str(video_path), str(cam_path), fps=15)

    return JSONResponse({
        "message": f"✅ Uploaded and extracted {len(files)} videos to {dataset_name}",
        "dataset": dataset_name
    })


@router.post("/process_multiview")
def process_multiview(dataset_name: str = Form(...)):
    dataset_path = f"data/multipleview/{dataset_name}"

    subprocess.run(["bash", "multipleviewprogress.sh", dataset_name], check=True, cwd=ROOT_DIR)

    subprocess.run([
        "python", "train.py",
        "-s", f"data/multipleview/{dataset_name}",
        "--port", "6017",
        "--expname", f"multipleview/{dataset_name}",
        "--configs", "arguments/multipleview/default.py"
    ], check=True, cwd=ROOT_DIR)

    subprocess.run([
        "python", "render.py",
        "--model_path", f"output/multipleview/{dataset_name}/",
        "--skip_train",
        "--configs", "arguments/multipleview/default.py"
    ], check=True, cwd=ROOT_DIR)


    video_url = f"http://localhost:8000/multiview_video/{dataset_name}/cam01.mp4"
    pointcloud_url = f"http://localhost:8000/multiview_pointcloud/{dataset_name}/points3D_multipleview.zip"

    return JSONResponse({
        "status": "processed",
        "dataset": dataset_name,
        "video_url": video_url,
        "pointcloud_url": pointcloud_url
    })


@router.get("/multiview_video/{dataset_name}/{filename}")
def get_multiview_video(dataset_name: str, filename: str):
    path = os.path.join(
        ROOT_DIR, "output", "multipleview", dataset_name, "video", "ours_14000", "video_rgb.mp4"
    )
    if not os.path.exists(path):
        return JSONResponse({"error": "Video not found."}, status_code=404)
    return FileResponse(path, media_type="video/mp4", filename=filename)


@router.get("/multiview_pointcloud/{dataset_name}/{filename}")
def get_multiview_pointcloud(dataset_name: str, filename: str):
    pointcloud_dir = os.path.join(
        ROOT_DIR, "output", "multipleview", dataset_name, "point_cloud", "iteration_14000"
    )

    if not os.path.exists(pointcloud_dir):
        return JSONResponse({"error": "Point cloud files not found."}, status_code=404)

    zip_output_path = f"/tmp/{dataset_name}_pointcloud.zip"
    if os.path.exists(zip_output_path):
        os.remove(zip_output_path)

    import zipfile
    with zipfile.ZipFile(zip_output_path, 'w') as zipf:
        for root, _, files in os.walk(pointcloud_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, pointcloud_dir)
                zipf.write(file_path, arcname)

    return FileResponse(
        zip_output_path,
        media_type="application/zip",
        filename=filename  # e.g., cam01_pointcloud.zip
    )

