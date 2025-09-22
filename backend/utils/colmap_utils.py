import os
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # your_project/routers
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "4DGaussians"))  # ../4DGaussians


def process_with_ns(colmap_output_dir: str, ns_output_dir: str):
    """
    用 NeRF Studio 的 ns-process-data 處理 COLMAP 輸出，
    並將 images 複製到 colmap/images 下。

    Parameters:
        colmap_output_dir (str): COLMAP 的輸出資料夾，例如 outputs/xxx
        ns_output_dir (str): NeRF Studio 要輸出的目錄，例如 nerf_data/xxx
    """
    os.makedirs(ns_output_dir, exist_ok=True)

    # Step 1: 執行 ns-process-data
    subprocess.run([
        "ns-process-data", "images",
        "--data", colmap_output_dir,
        "--output-dir", ns_output_dir
    ], check=True)

    # Step 2: 複製 images 到 colmap/images
    colmap_images_dir = os.path.join(ns_output_dir, "colmap")
    os.makedirs(colmap_images_dir, exist_ok=True)

    subprocess.run([
        "cp", "-r",
        os.path.join(ns_output_dir, "images"),
        colmap_images_dir
    ], check=True)
    
def run_4dgs_training(ns_data_dir: str, expname: str):
    """
    執行 4DGaussians 的 train.py

    Parameters:
        ns_data_dir (str): 資料位置（到 colmap 資料夾）
        expname (str): 實驗名稱（輸出會存在 logs/expname）
    """
    # base_dir = os.path.dirname(os.path.abspath(__file__))          # /your_project
    # parent_dir = os.path.abspath(os.path.join(base_dir, ".."))     # 回到 /
    # gaussians_dir = os.path.join(parent_dir, "4DGaussians")        # 4DGaussians 資料夾
    
    # 顯示當前 Conda 環境名稱（非必要，可註解掉）
    # print("📦 Current Conda environment:")
    # subprocess.run("echo $CONDA_DEFAULT_ENV", shell=True, executable="/bin/bash")
    
    print("ROOT_DIR:", ROOT_DIR)

    train_script = os.path.join(ROOT_DIR, "train.py")

    cmd = [
        "python", train_script,
        "-s", ns_data_dir,
        "--port", "6017",
        "--expname", expname,
        "--configs", os.path.join(ROOT_DIR, "arguments/hypernerf/default.py")
    ]

    print("🛠️ Running command:", " ".join(cmd))

    subprocess.run(cmd, check=True, cwd=ROOT_DIR)

def run_4dgs_rendering(model_output_dir: str):
    """
    執行 4DGaussians 的 render.py 進行渲染輸出

    Parameters:
        model_output_dir (str): 訓練完成後的 model 資料夾（例如 output/taskid）
    """
    import subprocess
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(base_dir, ".."))
    # gaussians_dir = os.path.join(parent_dir, "4DGaussians")

    render_script = os.path.join(ROOT_DIR, "render.py")

    cmd = [
        "python", render_script,
        "--model_path", model_output_dir,
        "--skip_train",
        "--configs", os.path.join(ROOT_DIR, "arguments/hypernerf/default.py")
    ]

    print("🎥 Running render command:", " ".join(cmd))

    subprocess.run(cmd, check=True, cwd=ROOT_DIR)
