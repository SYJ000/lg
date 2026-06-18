"""主入口"""

import json
from src.workflow import app
from src.state import AgentState


def run_prospecting_task(task: str):
    """运行拓客任务"""
    initial_state: AgentState = {
        "task": task,
        "task_type": "prospecting",
        "raw_data": [],
        "crawled_urls": [],
        "extracted_entities": [],
        "extraction_errors": [],
        "extraction_retry_count": 0,
        "tags": {},
        "tag_sources": {},
        "rag_results": [],
        "rag_query": "",
        "compliance_status": "",
        "risk_level": "",
        "risk_notes": [],
        "report": "",
        "report_generated": False,
        "human_review_required": False,
        "human_decision": None,
        "error_count": 0,
        "current_agent": "",
        "next_action": "",
    }

    result = app.invoke(initial_state)
    return result


if __name__ == "__main__":
    task = "帮我找重庆的农业科技企业"
    result = run_prospecting_task(task)
    print("最终报告：")
    print(result.get("report", "未生成报告"))
    print(f"\n是否需要人工审批：{result.get('human_review_required')}")