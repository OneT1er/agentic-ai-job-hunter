import csv
from pathlib import Path
from typing import Any, Dict, List

from src.logger import get_logger

logger = get_logger(__name__)


def export_to_csv(jobs: List[Dict[str, Any]], filepath: str = "ai_jobs_result.csv") -> None:
    if not jobs:
        logger.warning("未收集到有效数据，取消导出。")
        return

    logger.info("正在将 %d 条有效岗位信息导出至 %s...", len(jobs), filepath)

    fieldnames = jobs[0].keys()

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for job in jobs:
            processed = job.copy()
            if isinstance(processed.get("tech_tags"), list):
                processed["tech_tags"] = ", ".join(processed["tech_tags"])
            writer.writerow(processed)

    logger.info("CSV 导出完成！共 %d 条记录 -> %s", len(jobs), Path(filepath).absolute())
