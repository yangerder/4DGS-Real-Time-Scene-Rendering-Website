from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from utils import save_video_file
from fastapi.middleware.cors import CORSMiddleware
from video_utils import extract_frames_ffmpeg
from colmap_utils import run_colmap_pipeline, process_with_ns, run_4dgs_training, run_4dgs_rendering
from fastapi.responses import FileResponse
import shutil
import uuid, os


app = FastAPI()

# 加入這段 middleware 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 你也可以寫成 ["http://localhost:5173"] 比較安全
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_and_extract")
async def upload_and_extract(file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())

    # 儲存影片
    video_path = save_video_file(file, task_id)

    # 切成圖片
    frame_dir = f"outputs/{task_id}/images"
    extract_frames_ffmpeg(video_path, frame_dir)

    # 執行 COLMAP
    colmap_output_dir = f"outputs/{task_id}"
    run_colmap_pipeline(frame_dir, colmap_output_dir)##############################

    # 4. NeRF Studio 處理（你可以選用你想要的路徑）
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(base_dir, ".."))
    ns_output_dir = os.path.join(parent_dir, "4DGaussians", "data", task_id)
    process_with_ns(f"{colmap_output_dir}/images", ns_output_dir)########################
    
    # 這裡自動開始訓練！！
    ns_colmap_dir = os.path.join(ns_output_dir, "colmap")  # 注意要指到 colmap/
    run_4dgs_training(ns_colmap_dir, expname=task_id)##########################
    
    # 這裡新增渲染！
    model_output_dir = os.path.join("output", task_id)  # 這是4DGaussians下的output
    run_4dgs_rendering(model_output_dir)


    return JSONResponse({
        "task_id": task_id,
        "frames_dir": frame_dir,
        "colmap_output_dir": colmap_output_dir,
        "ns_output_dir": ns_output_dir,
        "message": "✅ 全部流程完成！（訓練＋渲染）"
    })
    
# 影片播放 API
@app.get("/get_video/{task_id}")
def get_video(task_id: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # your_project
    parent_dir = os.path.abspath(os.path.join(base_dir, ".."))  # / (上層)
    video_path = os.path.join(parent_dir, "4DGaussians", "output", task_id, "video", "ours_14000", "video_rgb.mp4")
    if not os.path.exists(video_path):
        return JSONResponse({"error": "Video not found."}, status_code=404)
    return FileResponse(video_path, media_type="video/mp4", filename=f"{task_id}_result.mp4")

# 點雲資料打包下載 API
@app.get("/download_pointcloud/{task_id}")
def download_pointcloud(task_id: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(base_dir, ".."))
    pointcloud_dir = os.path.join(parent_dir, "4DGaussians", "output", task_id, "point_cloud", "iteration_14000")
    if not os.path.exists(pointcloud_dir):
        return JSONResponse({"error": "Point cloud files not found."}, status_code=404)
    
    zip_output_path = f"/tmp/{task_id}_pointcloud.zip"

    # 重新壓縮
    if os.path.exists(zip_output_path):
        os.remove(zip_output_path)

    shutil.make_archive(zip_output_path.replace(".zip", ""), 'zip', pointcloud_dir)

    return FileResponse(zip_output_path, media_type="application/zip", filename=f"{task_id}_pointcloud.zip")
