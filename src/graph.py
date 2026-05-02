from langgraph.graph import END, StateGraph

from src.config import settings
from src.logger import get_logger
from src.nodes.evaluator import evaluator_node
from src.nodes.planner import planner_node
from src.nodes.scraper import scraper_node
from src.state import JobSearchState

logger = get_logger(__name__)


def _should_continue(state: JobSearchState) -> str:
    current = len(state["current_jobs"])
    iterations = state["iteration_count"]

    if current >= settings.target_job_count:
        logger.info("已达成收集目标 %d >= %d，任务结束！", current, settings.target_job_count)
        return "end"
    if iterations >= settings.max_iterations:
        logger.info("已达到最大迭代次数 %d，强制结束任务！", settings.max_iterations)
        return "end"

    return "continue"


def build_app():
    workflow = StateGraph(JobSearchState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("scraper", scraper_node)
    workflow.add_node("evaluator", evaluator_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "scraper")
    workflow.add_edge("scraper", "evaluator")

    workflow.add_conditional_edges(
        "evaluator",
        _should_continue,
        {"continue": "planner", "end": END},
    )

    return workflow.compile()
