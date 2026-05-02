# Agentic AI 校园招聘求职智能体

基于 **LangGraph** + **Playwright** + **大语言模型** 构建的自主求职 Agent。具备"规划 → 抓取 → 评估 → 循环"的 ReAct 工作流，专为 **AI Engineer / 算法工程师** 校园招聘设计。

## 核心特性

- **Agentic 工作流编排**: LangGraph 状态机，Planner → Scraper → Evaluator 三节点闭环
- **智能反反爬**: Playwright-Stealth 抹除浏览器指纹，支持懒加载滚动、多策略翻页
- **LLM 语义过滤**: Pydantic V2 结构化输出，精准区分校招/社招、技术岗/非技术岗
- **多平台切换**: 牛客网 ↔ 实习僧 动态轮换，分散风控压力
- **工程化完整**: pydantic-settings 配置、Rich 日志、Docker、CI、单元测试

## 项目结构

```
├── .github/workflows/ci.yml
├── src/
│   ├── config.py               # pydantic-settings 配置
│   ├── logger.py               # Rich 日志系统
│   ├── state.py                # 状态定义与 Pydantic 模型
│   ├── utils.py                # 工具函数
│   ├── nodes/
│   │   ├── planner.py          # 规划节点
│   │   ├── scraper.py          # 抓取节点
│   │   └── evaluator.py        # 评估节点
│   ├── prompts/
│   │   ├── planner.py          # Planner Prompt
│   │   └── evaluator.py        # Evaluator Prompt
│   ├── graph.py                # 图构建与路由
│   └── export.py               # CSV 导出
├── tests/
│   ├── test_utils.py
│   ├── test_state.py
│   └── test_export.py
├── main.py                     # 主入口
├── login.py                    # 登录鉴权脚本
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## 系统工作流

```
Planner 节点 → 调用 LLM 生成校招搜索关键词（失败时降级到本地备用词库）
     ↓
Scraper 节点 → Stealth 浏览器抓取岗位卡片（支持点击翻页 + URL 参数翻页）
     ↓
Evaluator 节点 → LLM 结构化输出，严格判别是否同时满足"AI技术方向 + 校园招聘"
     ↓
Router 路由 → 达标则导出 CSV 结束，未达标则回到 Planner 新一轮迭代
```

## 快速开始

### 1. 环境准备

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置

```bash
cp .env.example .env
# 编辑 .env，填入 LLM API Key 等信息
```

### 3. 运行

```bash
python main.py
```

### 4. Docker 运行

```bash
docker compose up
```

## 进阶：登录鉴权

部分平台限制未登录浏览页数。运行登录脚本手动扫码一次：

```bash
python login.py
```

浏览器弹出后完成登录，按回车保存 Cookie。此后运行 `main.py` 自动加载。

## 配置说明

所有可调参数见 `.env.example`：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | LLM API Key | 必填 |
| `OPENAI_BASE_URL` | LLM API 地址 | `https://api.openai.com/v1` |
| `MODEL_NAME` | 模型名称（需支持结构化输出） | `qwen/qwen3.5-9b` |
| `TARGET_JOB_COUNT` | 目标收集岗位数 | `50` |
| `MAX_ITERATIONS` | 最大迭代次数 | `20` |
| `HEADLESS` | 是否无头模式 | `true` |
| `MAX_PAGES_PER_QUERY` | 每个关键词最大翻页数 | `5` |
| `MAX_CARDS_PER_PAGE` | 每页最大卡片数 | `30` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

## License

MIT
