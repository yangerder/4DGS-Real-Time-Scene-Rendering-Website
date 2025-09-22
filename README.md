# 4D Gaussian Splatting With Motion-Aware Frame Selection

A system that preprocesses input images to accelerate 4DGS training.  
We implement the pipeline based on [hustvl/4DGaussians](https://github.com/hustvl/4DGaussians), but our method can be extended to other 4DGS construction frameworks.  
In addition, we provide a full-stack web system to automate 4D Gaussian Splatting (4DGS) reconstruction and rendering from single or multiple video uploads.

The slides for this project can be found [here](https://www.canva.com/design/DAGpF6ztpmY/t4J5H6Ur8jHppo1Q_P79wg/edit).

---

## Acceleration Method

<img width="1658" height="262" alt="image" src="https://github.com/user-attachments/assets/a537287e-0701-4635-b20d-4a4d0e5f8526" />

- Compute motion scores via optical flow to select training frames  
- Use different mapping methods (Linear, Square, Sigmoid, Log) for frame selection to accelerate training  
- Achieve up to **1.4× speed-up** with motion-aware frame sampling  

---

## Experiments Result
<img width="1002" height="533" alt="image" src="https://github.com/user-attachments/assets/0f6b7e79-550d-4b7a-a4c7-1362b45f1bc0" />

---

## Website Features

- Upload video(s) via web interface
- Automatically extract frames using ffmpeg
- Run COLMAP (SfM + MVS) for camera pose estimation and dense reconstruction
- Convert COLMAP results into NeRF Studio data format (`ns-process-data`)
- Train real-time 4D Gaussian Splatting models (`train.py`)
- Render output videos (`render.py`)
- Download point cloud files (`.pth`, `.ply`)
- Easy-to-use frontend with progress visualization and result preview
  
---


## Project Structure

```
├── backend/
│   ├── main.py          # FastAPI server
│   ├── utils.py         # File save helpers
│   ├── video_utils.py   # Frame extraction (ffmpeg)
│   ├── colmap_utils.py  # COLMAP + ns-process + training + rendering
│   ├── 4dgs_utils.py    # (Optional) Future expansion for 4DGS tools
│   └── requirements.txt # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main frontend upload page
│   │   └── ...
│   ├── public/
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json     # Frontend dependencies
└── 4DGaussians/          # Your 4DGS original repo (train.py, render.py, etc.)
└── gaussian-splatting-lightning/    # Web Viewer for 4DGS
```

---

##  Backend Setup (FastAPI)

### Install dependencies
(Assuming you already activated your 4DGaussians environment)

```bash
pip install fastapi uvicorn python-multipart aiofiles
```
### Start backend server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Frontend Setup (React + TailwindCSS)
### Install dependencies

```bash
npm install
```
### Start frontend

```bash
npm run dev
```
### Frontend Features

-  Video file upload  
-  Real-time progress bar  
-  Stage status updates  
  (uploading → frame extraction → COLMAP → training → rendering)  
-  Rendered video preview  
-  One-click download for point cloud data

---

## System Workflow
```
Upload Video
    ↓
Extract Frames (ffmpeg)
    ↓
Camera Pose Estimation & Dense Reconstruction (COLMAP)
    ↓
Data Conversion (ns-process-data)
    ↓
4D Gaussian Splatting Training (train.py)
    ↓
Rendering (render.py)
    ↓
Result Video Preview + Point Cloud Download
```

---

## Demo (Website Preview)

- Before Upload

  ![Before Upload](images/upload_progress_demo.png)
  
- Uploading (Progress)

  ![Uploading](images/uploading.png)  

- Upload Completed

  ![Upload Completed](images/upload_Completed.png)
  
- Video Preview & Point Cloud Download

  ![Video Preview and Download](images/video_download_preview_demo.png)
 
---

## License
This project is for research and educational purposes.
