"""Agentic AI 校园招聘求职智能体 — 主入口"""

from src.config import settings
from src.export import export_to_csv
from src.graph import build_app
from src.logger import get_logger
from src.state import JobSearchState

logger = get_logger(__name__)


def main() -> None:
    logger.info("启动 Agentic AI 求职系统 (目标: %d 个岗位)", settings.target_job_count)
    logger.info("=" * 60)

    app = build_app()

    initial_state: JobSearchState = {
        "target_count": settings.target_job_count,
        "current_jobs": [],
        "visited_urls": set(),
        "current_queries": [],
        "iteration_count": 0,
        "raw_html_data": [],
        "current_platform": "nowcoder",
    }

    final_state = app.invoke(initial_state)
    export_to_csv(final_state["current_jobs"])


if __name__ == "__main__":
    main()
