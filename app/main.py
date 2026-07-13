# app/main.py - FastAPI 入口
# 创建应用、注册路由、启动时初始化数据库

from fastapi import FastAPI
from app.routers import chat, sessions, agent, report
from app.database import init_db  # 导入数据库初始化

# 启动时初始化数据库
init_db()

app = FastAPI(
    title="LYAITEST AI测试平台",
    description="AI驱动的测试智能体平台",
    version="0.1.0"
)

# 注册路由
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(agent.router)
app.include_router(report.router)

@app.get("/")
def root():
    return {"message": "Hello from LYAITEST"}

@app.get("/health")
def health():
    return {"status": "ok"}