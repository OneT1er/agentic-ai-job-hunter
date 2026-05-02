import random
from typing import Any, Dict

from langchain_openai import ChatOpenAI

from src.config import settings
from src.logger import get_logger
from src.prompts.planner import (
    PLANNER_FALLBACK_POOL,
    PLANNER_INITIAL_QUERIES,
    PLANNER_SYSTEM_PROMPT,
)
from src.state import JobSearchState
from src.utils import contains_banned_terms, is_campus_query, safe_json_array_from_text

logger = get_logger(__name__)


def _create_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0.2,
    )


def planner_node(state: JobSearchState) -> Dict[str, Any]:
    logger.info(
        "第 %d 轮迭代 | 已收集: %d/%d",
        state["iteration_count"],
        len(state["current_jobs"]),
        state["target_count"],
    )

    queries = state.get("current_queries", [])

    if not queries:
        if state["iteration_count"] == 0:
            logger.info("系统启动，注入 AI Engineer 校招核心关键词...")
            return {"current_queries": list(PLANNER_INITIAL_QUERIES)}

        llm = _create_llm()
        try:
            response = llm.invoke(PLANNER_SYSTEM_PROMPT)
            new_queries = safe_json_array_from_text(response.content)

            valid_new: list[str] = []
            for q in new_queries:
                if len(q) < 3:
                    continue
                if "..." in q or "keyword" in q.lower():
                    continue
                if not is_campus_query(q):
                    continue
                if contains_banned_terms(q):
                    continue
                valid_new.append(q)

            if not valid_new:
                raise ValueError("生成结果均不满足校招约束")
            queries.extend(valid_new)
            logger.info("LLM 生成关键词: %s", queries)

        except Exception as e:
            logger.warning("策略生成失败 (%s)，启用备用词库...", e)
            queries = random.sample(PLANNER_FALLBACK_POOL, 3)

    logger.info("本轮下发执行关键词: %s", queries[0])
    return {"current_queries": queries}
