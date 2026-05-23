from typing import Dict, Any, List, TypedDict

from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

from app.services.llm_service import get_llm
from app.agents.allocation_agent import allocate_orders_to_vehicles
from app.agents.traffic_agent import apply_traffic
from app.agents.eta_agent import estimate_route_eta

# Define the state for LangGraph
class RouteState(TypedDict, total=False):
    payload: Dict[str, Any]
    constraints: str
    segments: List[Dict[str, Any]]
    total_eta_min: float
    reasoning: str

llm = get_llm()

@tool
def allocation_tool(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Allocate orders to vehicles and produce route segments."""
    return allocate_orders_to_vehicles(payload)

@tool
def traffic_tool(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply traffic adjustments to route segments."""
    return apply_traffic(segments)

@tool
def eta_tool(segments: List[Dict[str, Any]]) -> float:
    """Estimate total ETA in minutes for given route segments."""
    return estimate_route_eta(segments)


def _load_prompt() -> str:
    prompt_path = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "prompts"
        / "optimization_prompt.txt"
    )
    return prompt_path.read_text(encoding="utf-8")


def build_graph():
    graph = StateGraph(RouteState)

    def call_allocation(state: RouteState) -> RouteState:
        segments = allocation_tool.invoke({"payload": state["payload"]})
        state["segments"] = segments
        return state

    def call_traffic(state: RouteState) -> RouteState:
        adjusted = traffic_tool.invoke({"segments": state["segments"]})
        state["segments"] = adjusted
        return state

    def call_eta(state: RouteState) -> RouteState:
        total_eta = eta_tool.invoke({"segments": state["segments"]})
        state["total_eta_min"] = total_eta
        return state

    def call_llm_summary(state: RouteState) -> RouteState:
        base_prompt = _load_prompt()
        constraints = state.get("constraints", "")
        segments = state["segments"]
        total_eta = state["total_eta_min"]

        content = (
            f"{base_prompt}\n\n"
            f"User constraints: {constraints}\n"
            f"Route segments:\n{segments}\n"
            f"Total ETA (minutes): {total_eta:.2f}\n"
            "Explain briefly why this route plan is reasonable."
        )

        try:
            resp = llm.invoke(content)
            state["reasoning"] = resp.content
        except Exception as e:
            # Fallback when LLM call fails (e.g., quota exceeded)
            state["reasoning"] = (
                "LLM-based explanation unavailable (error: "
                f"{type(e).__name__}). "
                "Using deterministic reasoning: round-robin allocation with "
                "traffic-adjusted ETAs based on the trained model."
            )

        return state

    graph.add_node("allocation", call_allocation)
    graph.add_node("traffic", call_traffic)
    graph.add_node("eta", call_eta)
    graph.add_node("llm_summary", call_llm_summary)

    graph.set_entry_point("allocation")
    graph.add_edge("allocation", "traffic")
    graph.add_edge("traffic", "eta")
    graph.add_edge("eta", "llm_summary")
    graph.add_edge("llm_summary", END)

    return graph.compile()


graph = build_graph()

def print_graph_ascii() -> None:
    """
    Print an ASCII representation of the LangGraph orchestrator.
    """
    underlying = graph.get_graph()
    print(underlying.draw_ascii())

def print_graph_mermaid() -> None:
    """
    Print Mermaid code for the LangGraph orchestrator.
    You can paste this into https://mermaid.live to see a rendered diagram.
    """
    underlying = graph.get_graph()
    mermaid_code = underlying.draw_mermaid()
    print(mermaid_code)

def optimize_routes_with_llm(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for LLM-based orchestration.
    """
    constraints = payload.get("constraints", "") or ""
    initial_state: RouteState = {"payload": payload, "constraints": constraints}
    final_state = graph.invoke(initial_state)

    routes: Dict[str, List[Dict[str, Any]]] = {}
    for seg in final_state["segments"]:
        vid = seg["vehicle_id"]
        routes.setdefault(vid, []).append(seg)

    return {
        "routes": routes,
        "total_eta_min": final_state["total_eta_min"],
        "reasoning": final_state["reasoning"],
    }

