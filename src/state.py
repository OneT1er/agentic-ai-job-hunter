
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class JobSearchState(TypedDict):
    target_count: int
    current_jobs: list[dict]
    visited_urls: set[str]
    current_queries: list[str]
    iteration_count: int
    raw_html_data: list[dict]
    current_platform: str


class JobExtraction(BaseModel):
    is_target_job: bool = Field(
        description="核心校验：是否明确为AI/大模型/算法相关，且面向校招或实习。"
    )
    title: str = Field(description="职位名称", default="")
    company: str = Field(description="公司名称", default="")
    location: str = Field(description="工作地点", default="未知")
    salary: str = Field(description="薪资范围", default="面议")
    tech_tags: list[str] = Field(
        description="技术栈关键词，如 PyTorch, LLM 等", default_factory=list
    )
    requirements: str = Field(
        description="用一句话总结岗位的核心技术要求", default=""
    )
