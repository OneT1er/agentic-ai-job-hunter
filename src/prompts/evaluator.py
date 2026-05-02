EVALUATOR_SYSTEM_PROMPT = """请从以下岗位文本中抽取信息并判断是否属于"AI Engineer校园招聘岗位"：

岗位文本：
{job_text}

判定规则（必须严格执行）：
A. is_target_job=true 必须同时满足：
   1) 技术方向相关：文本中应体现 AI Engineer/人工智能/机器学习/深度学习/LLM/NLP/CV/算法工程 等方向之一；
   2) 校园招聘相关：文本中应体现 校招/校园招聘/应届生/毕业生/xx届(如2026届)/秋招/春招 等信号之一。
B. 若非目标岗位，is_target_job=false。
C. 明确实习、社招、兼职、外包、销售、行政、人事等非目标岗位，is_target_job=false。
D. 输出字段保持结构化，title/company/location/description 尽量提取；无法确定可留空，但不要编造。"""
