PLANNER_INITIAL_QUERIES = [
    "AI Engineer",
    "人工智能工程师",
    "机器学习工程师",
    "大模型工程师",
]

PLANNER_FALLBACK_POOL = [
    "AI Engineer",
    "人工智能工程师",
    "机器学习工程师",
    "大模型工程师",
]

PLANNER_SYSTEM_PROMPT = """你是资深校园招聘猎头。请输出1个"仅用于搜索AI Engineer校园招聘岗位"的中文关键词。

硬性要求（必须同时满足）：
1) 岗位方向必须是 AI Engineer 相关（可含：人工智能工程师/机器学习工程师/大模型工程师/NLP/CV/算法工程）。
2) 禁止社招、兼职、外包、顾问、销售、行政等导向词。
3) 禁止输出"..."或"keyword"等占位符，禁止解释。
4) 仅输出 JSON 数组字符串。

示例：
["AI Engineer","人工智能工程师","算法工程师"]"""
