import subprocess


# 僅指定 Conda 環境對應的 Python 執行路徑
ENV_PYTHON_PATHS = {
    "willi_gspl": "/home/amazon/anaconda3/envs/willi_gspl/bin/python",
    "Gaussians4D": "/home/amazon/anaconda3/envs/Gaussians4D/bin/python"
}

def run_in_conda_env(env_name: str, script_path: str, script_args: list = None) -> dict:
    if env_name not in ENV_PYTHON_PATHS:
        return {"status": "error", "message": f"Unknown environment: {env_name}"}

    python_path = ENV_PYTHON_PATHS[env_name]
    cmd = [python_path, script_path]
    if script_args:
        cmd.extend(script_args)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Execution timed out."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# VIEWER_DIR = "/media/amazon/F/willi/4dgs/gaussian-splatting-lightning"
# conda activate willi_gspl 
# run python viewer.py /media/amazon/F/willi/4dgs/4DGaussians/output/dynerf/cut_roasted_beef --vanilla_gs4d --host 0.0.0.0 --port 8081
# 在 VIEWER_DIR 執行


import subprocess
import os

ENV_PYTHON_PATHS = {
    "willi_gspl": "/home/amazon/anaconda3/envs/willi_gspl/bin/python",
    "Gaussians4D": "/home/amazon/anaconda3/envs/Gaussians4D/bin/python"
}


def launch_viewer(task_id: str, env: str = "willi_gspl", port: int = 8081):
    viewer_dir = "/media/amazon/F/willi/4dgs/gaussian-splatting-lightning"
    output_dir = f"/media/amazon/F/willi/4dgs/4DGaussians/output/{task_id}"

    if env not in ENV_PYTHON_PATHS:
        raise ValueError(f"Unknown environment: {env}")

    python_path = ENV_PYTHON_PATHS[env]

    cmd = [
        python_path,
        "viewer.py",
        output_dir,
        "--vanilla_gs4d",
        "--host", "0.0.0.0",
        "--port", str(port)
    ]

    subprocess.Popen(cmd, cwd=viewer_dir)
    print(f"🚀 Launched viewer for {task_id} using env '{env}' on port {port}")
