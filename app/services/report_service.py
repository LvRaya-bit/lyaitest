# app/services/report_service.py
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from app.models.report import TestReport

logger = logging.getLogger(__name__)

# 内存存储（项目重启会丢失，后续可换数据库）
reports_store: list = []

def save_report(report_data: dict) -> TestReport:
    """保存测试报告"""
    try:
        report = TestReport(
            id=str(uuid.uuid4())[:8],
            session_id=report_data.get("session_id", "unknown"),
            test_type=report_data.get("test_type", "unknown"),
            url=report_data.get("url", ""),
            status_code=report_data.get("status_code"),
            response_time=report_data.get("response_time"),
            title=report_data.get("title"),
            screenshot=report_data.get("screenshot"),
            error=report_data.get("error"),
            created_at=datetime.now()
        )
        reports_store.append(report)
        logger.info(f"[save_report] 成功保存报告 id={report.id}, store_len={len(reports_store)}, store_id={id(reports_store)}")
        return report
    except Exception as e:
        logger.error(f"[save_report] 保存报告失败: {e}, report_data={report_data}")
        raise

def get_reports_by_session(session_id: str) -> List[TestReport]:
    """获取某个会话的所有测试报告"""
    return [r for r in reports_store if r.session_id == session_id]

def get_all_reports() -> List[TestReport]:
    """获取所有测试报告"""
    logger.info(f"[get_all_reports] 当前报告数量: {len(reports_store)}, store_id={id(reports_store)}")
    return reports_store

def get_report_by_id(report_id: str) -> Optional[TestReport]:
    """根据ID获取报告"""
    for r in reports_store:
        if r.id == report_id:
            return r
    return None
