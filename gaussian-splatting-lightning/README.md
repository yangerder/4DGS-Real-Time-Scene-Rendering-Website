
# 4D Gaussian Splatting Web Viewer Setup

This project uses [gaussian-splatting-lightning](https://github.com/yzslab/gaussian-splatting-lightning) as the viewer for 4D Gaussian Splatting (4DGS).

## Clone Repository

Clone the official repository into this folder:

```bash
git clone https://github.com/yzslab/gaussian-splatting-lightning.git
cd gaussian-splatting-lightning
```

## Create conda env

```bash
conda create -yn willi_gspl python=3.9 pip
conda activate willi_gspl
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements.txt
pip install "numpy<2.0"
pip install --upgrade viser
```
