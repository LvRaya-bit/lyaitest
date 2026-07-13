# app/routers/report.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.services.report_service import get_all_reports, get_reports_by_session, get_report_by_id
from app.models.report import TestReport

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

@router.get("/", response_model=List[TestReport])
async def list_reports():
    """获取所有测试报告"""
    return get_all_reports()

@router.get("/session/{session_id}", response_model=List[TestReport])
async def get_reports_by_session_route(session_id: str):
    """获取指定会话的所有测试报告"""
    reports = get_reports_by_session(session_id)
    if not reports:
        raise HTTPException(status_code=404, detail="未找到该会话的报告")
    return reports

@router.get("/{report_id}", response_model=TestReport)
async def get_report(report_id: str):
    """根据ID获取测试报告"""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report