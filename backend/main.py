from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import singleview, multiview

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 註冊路由模組
app.include_router(singleview.router)
app.include_router(multiview.router)
