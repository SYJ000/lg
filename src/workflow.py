from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents import run_prospecting, run_policy_advisor, run_reviewer


def decide_next(state: AgentState) -> str:
    action = state.get("next_action", "")
    if action == "to_reviewer":
        return "reviewer"
    elif action == "back_to_collector":
        return "back_to_collector"
    elif action == "done":
        return "done"
    else:
        return "done"


def build_workflow() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("prospecting", run_prospecting)
    graph.add_node("policy_advisor", run_policy_advisor)
    graph.add_node("reviewer", run_reviewer)
    graph.add_node("human_review", lambda s: s)

    graph.set_entry_point("prospecting")

    graph.add_conditional_edges("prospecting", decide_next, {
        "reviewer": "reviewer",
        "back_to_collector": "prospecting",
        "done": "human_review",
    })
    graph.add_conditional_edges("reviewer", decide_next, {
        "done": "human_review",
        "back_to_collector": "prospecting",
    })
    graph.add_conditional_edges("policy_advisor", decide_next, {
        "done": "human_review",
    })

    graph.add_edge("human_review", END)

    return graph.compile()


app = build_workflow()