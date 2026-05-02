import re

import json5


def safe_json_array_from_text(text: str) -> list[str]:
    """从模型输出中健壮提取 JSON 数组，优先使用 json5 解析。"""
    clean = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    try:
        result = json5.loads(clean)
        if isinstance(result, list):
            return [str(x).strip() for x in result if str(x).strip()]
    except (ValueError, TypeError):
        pass

    match = re.search(r"\[[\s\S]*\]", clean)
    if not match:
        raise ValueError(f"未能从文本中提取 JSON 数组: {clean[:200]}")
    arr = json5.loads(match.group())
    return [str(x).strip() for x in arr if str(x).strip()]


def is_campus_query(q: str) -> bool:
    """检查关键词是否包含校园招聘信号词。"""
    tokens = ["校招", "校园招聘", "应届", "毕业生", "届"]
    return any(t in q for t in tokens)


def normalize_url(href: str, platform_key: str) -> str:
    """将相对路径补全为完整 URL。"""
    if not href:
        return ""
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return f"https://www.{platform_key}.com{href}"


BANNED_TERMS = ["实习", "社招", "兼职", "销售", "行政", "外包"]


def contains_banned_terms(q: str) -> bool:
    """检查是否包含禁止的关键词。"""
    return any(b in q for b in BANNED_TERMS)
