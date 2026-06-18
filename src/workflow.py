"""LangGraph 工作流主文件"""

from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents import run_prospecting, run_policy_advisor, run_reviewer


def decide_next(state: AgentState) -> str:
    """路由决策：根据当前状态决定下一个节点"""
    action = state.get("next_action", "")

    if action == "to_reviewer":
        return "reviewer"
    elif action == "back_to_collector":
        return "prospecting"          # 循环边：退回拓客助手
    elif action == "done":
        return "human_review"
    else:
        return "human_review"


def build_workflow() -> StateGraph:
    """构建 LangGraph StateGraph"""
    graph = StateGraph(AgentState)

    # 注册节点
    graph.add_node("prospecting", run_prospecting)    # Agent A
    graph.add_node("policy_advisor", run_policy_advisor)  # Agent B
    graph.add_node("reviewer", run_reviewer)           # Agent C
    graph.add_node("human_review", lambda s: s)        # 终态（挂起等人工）

    # 入口
    graph.set_entry_point("prospecting")

    # 正常流程：拓客 → 审核 → 人工
    graph.add_conditional_edges("prospecting", decide_next, {
        "to_reviewer": "reviewer",
        "back_to_collector": "prospecting",  # 循环边
        "reviewer": "reviewer",
        "done": "human_review",
    })
    graph.add_conditional_edges("reviewer", decide_next, {
        "done": "human_review",
        "back_to_collector": "prospecting",  # 审核不达标退回
    })

    # 政策顾问独立走
    graph.add_conditional_edges("policy_advisor", decide_next, {
        "done": "human_review",
    })

    # 终态
    graph.add_edge("human_review", END)

    return graph.compile()


# 构建可执行图
app = build_workflow()