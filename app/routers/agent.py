# app/routers/agent.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.agent import run_agent

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

class AgentRequest(BaseModel):
    message: str
    session_id: str  # 新增

class AgentResponse(BaseModel):
    reply: str

@router.post("/", response_model=AgentResponse)
async def agent_chat(request: AgentRequest):
    try:
        result = run_agent(request.message, request.session_id)  # 把 session_id 传给 run_agent
        return AgentResponse(reply=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))