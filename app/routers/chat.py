from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from app.storage import messages_store

load_dotenv()

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str  # 新增

class ChatResponse(BaseModel):
    reply: str

llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0.3
)

# ========== 普通接口（一次性返回） ==========
@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. 检查会话是否存在
    if request.session_id not in messages_store:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 2. 读取该会话的历史消息
    history = messages_store[request.session_id]
    context = ""
    for msg in history:
        context += f"{msg['role']}: {msg['content']}\n"
    context += f"user: {request.message}\n"
    
    # 3. 调用模型
    response = llm.invoke(context)
    
    # 4. 保存本次对话到历史
    messages_store[request.session_id].append({"role": "user", "content": request.message})
    messages_store[request.session_id].append({"role": "assistant", "content": response.content})
    
    return ChatResponse(reply=response.content)

# ========== 流式接口（逐字返回） ==========
@router.post("/stream")
async def chat_stream(request: ChatRequest):
    if request.session_id not in messages_store:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    async def generate():
        # 读取历史
        history = messages_store[request.session_id]
        context = ""
        for msg in history:
            context += f"{msg['role']}: {msg['content']}\n"
        context += f"user: {request.message}\n"
        
        # 保存用户消息
        messages_store[request.session_id].append({"role": "user", "content": request.message})
        
        # 流式调用
        full_response = ""
        async for chunk in llm.astream(context):
            full_response += chunk.content
            yield f"data: {chunk.content}\n\n"
        
        # 保存 AI 回复
        messages_store[request.session_id].append({"role": "assistant", "content": full_response})
    
    
    # 使用 text/event-stream 媒体类型，符合 SSE 标准
    return StreamingResponse(generate(), media_type="text/event-stream")