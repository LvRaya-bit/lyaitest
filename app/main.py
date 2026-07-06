from fastapi import FastAPI
from app.routers import chat  # 新增

app = FastAPI(
    title="LYAITEST AI测试平台",
    description="AI驱动的测试智能体平台",
    version="0.1.0"
)

# 注册路由
app.include_router(chat.router)  # 新增

@app.get("/")
def root():
    return {"message": "Hello from LYAITEST"}

@app.get("/health")
def health():
    return {"status": "ok"}