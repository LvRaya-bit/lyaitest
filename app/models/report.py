# app/models/report.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TestReport(BaseModel):
    """测试报告数据模型"""
    id: str                    # 报告唯一ID
    session_id: str            # 所属会话ID
    test_type: str             # 测试类型: "api" 或 "web"
    url: str                   # 测试的URL
    status_code: Optional[int] = None      # HTTP状态码
    response_time: Optional[float] = None  # 响应时间(秒)
    title: Optional[str] = None            # 页面标题(Web测试)
    screenshot: Optional[str] = None       # 截图路径(Web测试)
    error: Optional[str] = None            # 错误信息
    created_at: datetime = datetime.now()  # 创建时间