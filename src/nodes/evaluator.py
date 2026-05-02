from typing import Any

from langchain_openai import ChatOpenAI

from src.config import settings
from src.logger import get_logger
from src.prompts.evaluator import EVALUATOR_SYSTEM_PROMPT
from src.state import JobExtraction, JobSearchState

logger = get_logger(__name__)


def _create_evaluator_llm():
    llm = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openai_api_key,  # type: ignore[arg-type]
        base_url=settings.openai_base_url,
        temperature=0.2,
    )
    return llm.with_structured_output(JobExtraction)


def evaluator_node(state: JobSearchState) -> dict[str, Any]:
    valid_jobs = state.get("current_jobs", [])
    visited_urls = state.get("visited_urls", set())
    raw_data = state.get("raw_html_data", [])

    if not raw_data:
        return {
            "current_jobs": valid_jobs,
            "visited_urls": visited_urls,
            "iteration_count": state["iteration_count"] + 1,
            "raw_html_data": [],
        }

    logger.info("正在进行 AI Engineer 校招语义质检...")
    llm = _create_evaluator_llm()

    for item in raw_data:
        url = item.get("url", "")
        if not url:
            continue
        if url in visited_urls:
            continue
        visited_urls.add(url)

        prompt = EVALUATOR_SYSTEM_PROMPT.format(job_text=item.get("text", ""))

        try:
            result = llm.invoke(prompt)
            if result.is_target_job:  # type: ignore[attr-defined, union-attr]
                job_info = result.model_dump()
                job_info.pop("is_target_job", None)
                job_info.update({
                    "job_url": url,
                    "source": item.get("source", ""),
                })
                valid_jobs.append(job_info)
                logger.info(
                    "  [校招命中] %s @ %s",
                    job_info.get("title", "未知岗位"),
                    job_info.get("company", "未知公司"),
                )
        except Exception as e:
            logger.warning("评估失败 (url=%s): %s", url[:60], e)

    return {
        "current_jobs": valid_jobs,
        "visited_urls": visited_urls,
        "iteration_count": state["iteration_count"] + 1,
        "raw_html_data": [],
    }
