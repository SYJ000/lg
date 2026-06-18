"""Agent 节点定义：拓客助手、政策顾问、审核员"""

from src.state import AgentState
from src.tools import (
    crawl_procurement, crawl_company_detail,
    extract_entities, extract_query_structured,
    apply_rule_engine,
    rag_search, rag_precheck,
    generate_report,
)
from src.tools import _call_llm

# ============================================================
# Agent A：拓客助手
# ============================================================

def run_prospecting(state: AgentState) -> AgentState:
    """拓客助手：采集 → 抽取 → 打标 → 预检"""
    state["current_agent"] = "collector"

    # Step 1: 爬取数据
    raw = crawl_procurement("农业科技", "重庆")
    state["raw_data"] = raw

    # Step 2: 实体抽取
    entities = []
    errors = []
    for item in raw:
        try:
            entity = extract_entities(item.get("title", ""))
            entities.append(entity)
        except Exception as e:
            errors.append(str(e))

    state["extracted_entities"] = entities
    state["extraction_errors"] = errors

    # 如果抽取失败超过阈值，递增错误计数（LangGraph 循环边检测到后触发重试）
    if errors:
        state["error_count"] = state.get("error_count", 0) + 1

    # Step 3: 规则引擎打标
    if entities:
        state["tags"] = apply_rule_engine(entities[0])

    # Step 4: 合规预检
    if entities:
        precheck = rag_precheck(entities[0])
        state["rag_results"] = [{"precheck": precheck}]

    # 判断是否需要转审核员
    state["next_action"] = "to_reviewer"
    return state


# ============================================================
# Agent B：政策顾问
# ============================================================

def run_policy_advisor(state: AgentState) -> AgentState:
    """政策顾问：问题结构化 → RAG 检索 → 生成回答"""
    state["current_agent"] = "policy_advisor"

    # Step 1: 将问题转为结构化查询
    query = extract_query_structured(state["task"])
    state["rag_query"] = query.get("keywords", state["task"])

    # Step 2: RAG 检索
    results = rag_search(state["rag_query"])
    state["rag_results"] = results

    # Step 3: 14B 组装回答
    prompt = f"""
问题：{state['task']}
检索到的政策条文：{results}
请生成带原文引用的回答。
"""
    state["report"] = _call_llm(prompt)
    state["report_generated"] = True
    state["next_action"] = "done"
    return state


# ============================================================
# Agent C：审核员
# ============================================================

def run_reviewer(state: AgentState) -> AgentState:
    """审核员：交叉验证 → 深度合规 → 风险判定 → 生成报告"""
    state["current_agent"] = "reviewer"

    # Step 1: 交叉验证（简化：检查 error_count）
    if state.get("error_count", 0) > 3:
        state["next_action"] = "back_to_collector"  # 触发循环边退回
        return state

    # Step 2: 深度合规审核
    deep_check = rag_search(
        f"{state['extracted_entities'][0].get('company_name','')} 政策限制 风险评估"
        if state.get("extracted_entities") else state["task"]
    )
    state["rag_results"] = deep_check

    # Step 3: 风险等级判定
    if state.get("extracted_entities"):
        entity = state["extracted_entities"][0]
        if entity.get("risk_level") == "高":
            state["risk_level"] = "high"
            state["human_review_required"] = True   # 触发 Breakpoint
        else:
            state["risk_level"] = "low"
            state["human_review_required"] = False

    # Step 4: 生成报告
    state["report"] = generate_report(state)
    state["report_generated"] = True
    state["next_action"] = "done"
    return state