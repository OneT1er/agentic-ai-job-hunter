from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM 配置
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    model_name: str = "qwen/qwen3.5-9b"

    # 任务配置
    target_job_count: int = 50
    max_iterations: int = 20

    # 爬虫配置
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    headless: bool = True
    max_pages_per_query: int = 5
    max_cards_per_page: int = 30

    # 日志
    log_level: str = "INFO"


settings = Settings()
