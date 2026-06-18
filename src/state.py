"""全局状态定义"""

from typing import TypedDict, Optional, Any

class AgentState(TypedDict):
    """LangGraph 全局状态字典"""

    # 任务信息
    task: str                              # 用户原始输入
    task_type: str                         # 任务类型: prospecting / policy / review

    # 数据采集阶段
    raw_data: list[dict]                   # 爬虫采集的原始数据
    crawled_urls: list[str]                # 已采集的 URL 列表

    # 实体抽取阶段
    extracted_entities: list[dict]         # 7B 抽取的结构化实体
    extraction_errors: list[str]           # 抽取异常记录
    extraction_retry_count: int            # 重试次数

    # 打标阶段
    tags: dict                             # 规则引擎打的标签
    tag_sources: dict                      # 每个标签的依据

    # RAG 检索阶段
    rag_results: list[dict]                # RAG 检索结果
    rag_query: str                         # RAG 查询语句

    # 审核阶段
    compliance_status: str                 # 合规状态: pass / fail / pending
    risk_level: str                        # 风险等级: high / mid / low
    risk_notes: list[str]                  # 风险备注

    # 报告阶段
    report: str                            # 最终审核报告
    report_generated: bool                 # 是否已生成报告

    # 人工审批
    human_review_required: bool            # 是否需要人工审批
    human_decision: Optional[str]          # 人工决策: approve / reject / None

    # 流程控制
    error_count: int                       # 累计错误次数
    current_agent: str                     # 当前 Agent: collector / evaluator / reviewer
    next_action: str                       # 下一步动作