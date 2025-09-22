# routers/singleview.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
# routers/singleview.py
from utils.video_utils import save_video_file
from utils.colmap_utils import  process_with_ns, run_4dgs_training, run_4dgs_rendering
import os, uuid, shutil
from utils.utils import launch_viewer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # your_project/routers
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "4DGaussians"))  # ../4DGaussians

router = APIRouter()

@router.post("/upload_and_extract")
async def upload_and_extract(file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    video_path = save_video_file(file, task_id)

    # 1. 執行 motion.py → 動態採樣影格
    motion_script = os.path.join(ROOT_DIR, "motion.py")

    cmd = [
        "python", motion_script,
        "--videos", video_path,
        "--dataset_name", task_id,
        "--method", "square"
    ]

    print(f"📽️ Running motion.py for {task_id}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ motion.py failed:")
        print(result.stderr)
        return JSONResponse({"error": "Failed to extract frames with motion.py"}, status_code=500)
    else:
        print("✅ motion.py completed")
        print(result.stdout)


    ns_output_dir = os.path.join(ROOT_DIR, "data", task_id)

    process_with_ns(f"data/{task_id}/images", ns_output_dir)

    ns_colmap_dir = os.path.join(ns_output_dir, "colmap")
    run_4dgs_training(ns_colmap_dir, expname=task_id)

    model_output_dir = os.path.join("output", task_id)
    run_4dgs_rendering(model_output_dir)
    
    launch_viewer(task_id, env="willi_gspl")

    return JSONResponse({
        "task_id": task_id,
        "ns_output_dir": ns_output_dir,
        "message": "✅ 全部流程完成！（訓練＋渲染）"
    })


@router.get("/get_video/{task_id}")
def get_video(task_id: str):
    path = f"../4DGaussians/output/{task_id}/video/ours_14000/video_rgb.mp4"
    if not os.path.exists(path):
        return JSONResponse({"error": "Video not found."}, status_code=404)
    return FileResponse(path, media_type="video/mp4", filename=f"{task_id}_result.mp4")


@router.get("/download_pointcloud/{task_id}")
def download_pointcloud(task_id: str):
    pointcloud_dir = f"../4DGaussians/output/{task_id}/point_cloud/iteration_14000"
    if not os.path.exists(pointcloud_dir):
        return JSONResponse({"error": "Point cloud files not found."}, status_code=404)

    zip_output_path = f"/tmp/{task_id}_pointcloud.zip"
    if os.path.exists(zip_output_path):
        os.remove(zip_output_path)

    shutil.make_archive(zip_output_path.replace(".zip", ""), 'zip', pointcloud_dir)
    return FileResponse(zip_output_path, media_type="application/zip", filename=f"{task_id}_pointcloud.zip")


import subprocess
import os
from fastapi import HTTPException
import socket
import time

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

ENV_PYTHON_PATHS = {
    "willi_gspl": "/home/amazon/anaconda3/envs/willi_gspl/bin/python",
    "Gaussians4D": "/home/amazon/anaconda3/envs/Gaussians4D/bin/python"
}

viewer_process = None

@router.post("/launch_viewer/{task_id:path}")
def launch_viewer(task_id: str, env: str = "willi_gspl", port: int = 8081):
    global viewer_process
    
    
    viewer_dir = "/media/amazon/F/willi/4dgs/gaussian-splatting-lightning"
    output_dir = f"/media/amazon/F/willi/4dgs/4DGaussians/output/{task_id}"

    if env not in ENV_PYTHON_PATHS:
        raise HTTPException(status_code=400, detail=f"Unknown environment: {env}")

    if not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail=f"Output directory not found: {output_dir}")

    python_path = ENV_PYTHON_PATHS[env]
    viewer_script = os.path.join(viewer_dir, "viewer.py")

    cmd = [
        python_path,
        viewer_script,
        output_dir,
        "--vanilla_gs4d",
        "--host", "0.0.0.0",
        "--port", str(port)
    ]
    
    # 🛑 若前一個 viewer 還在，先 kill 掉
    if viewer_process and viewer_process.poll() is None:
        print("🧹 Killing previous viewer...")
        viewer_process.terminate()
        time.sleep(1)
            
        # 執行前先確認 port 沒被卡住
        if is_port_in_use(port):
            print(f"⛔ Port {port} is already in use. Checking if viewer process is running...")
            raise HTTPException(status_code=500, detail=f"Port {port} is still in use. Viewer may not have terminated cleanly.")

        try:
            viewer_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            viewer_process.kill()
            print("⛔ Force killed viewer process.")

    try:
        viewer_process = subprocess.Popen(cmd, cwd=viewer_dir)
        print(f"🚀 Launched viewer for {task_id} using env '{env}' on port {port}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "status": "launched",
        "env": env,
        "port": port,
        "viewer_url": f"http://localhost:{port}/"
    }