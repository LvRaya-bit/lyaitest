from pydantic import BaseModel
from typing import Optional, List

# ============================================
# 第1个模型：创建会话时客户端传入的数据
# ============================================
class SessionCreate(BaseModel):
    """创建会话请求体"""
    name: Optional[str] = None
    # name 是可选字段，客户端可以不传
    # 不传的话服务器会自动生成一个名字

# ============================================
# 第2个模型：返回给客户端的会话数据
# ============================================
class SessionResponse(BaseModel):
    """会话响应体"""
    session_id: str    # 会话ID，由服务器生成
    name: str          # 会话名称
    created_at: str    # 创建时间

# ============================================
# 第3个模型：返回给客户端的消息数据
# ============================================
class MessageResponse(BaseModel):
    """消息响应体"""
    role: str          # "user" 或 "assistant"
    content: str       # 消息内容