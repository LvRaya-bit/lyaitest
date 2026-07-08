from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from datetime import datetime

from app.models.session import SessionCreate, SessionResponse, MessageResponse
from app.storage import sessions_store, messages_store

# ============================================
# 创建路由分组
# ============================================
router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

# ============================================
# 接口1：创建会话
# ============================================
@router.post("/", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    # 1. 生成唯一ID（8位随机字符串）
    session_id = str(uuid.uuid4())[:8]
    
    # 2. 处理会话名称：如果客户端没传，自动生成
    name = request.name or f"会话_{session_id}"
    
    # 3. 记录创建时间
    created_at = datetime.now().isoformat()
    
    # 4. 保存到 sessions_store
    sessions_store[session_id] = {
        "name": name,
        "created_at": created_at
    }
    
    # 5. 为这个会话初始化空历史
    messages_store[session_id] = []
    
    # 6. 返回给客户端
    return SessionResponse(
        session_id=session_id,
        name=name,
        created_at=created_at
    )

# ============================================
# 接口2：获取所有会话列表
# ============================================
@router.get("/", response_model=List[SessionResponse])
async def list_sessions():
    result = []
    for session_id, data in sessions_store.items():
        result.append(SessionResponse(
            session_id=session_id,
            name=data["name"],
            created_at=data["created_at"]
        ))
    return result

# ============================================
# 接口3：获取某个会话的历史消息
# ============================================
@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(session_id: str):
    # 检查会话是否存在
    if session_id not in messages_store:
        raise HTTPException(status_code=404, detail="会话不存在")
    return messages_store[session_id]

# ============================================
# 接口4：删除会话
# ============================================
@router.delete("/{session_id}")
async def delete_session(session_id: str):
    # 检查会话是否存在
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 同时删除会话信息和历史消息
    del sessions_store[session_id]
    del messages_store[session_id]
    
    return {"message": "会话已删除"}