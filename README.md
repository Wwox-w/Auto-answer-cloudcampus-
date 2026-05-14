# Auto-answer

基于 LLM 的智能答题助手，适用于东北林业大学云校园（Moodle）在线答题平台。

## 功能

- **自动解析题目** — 从网页中提取选择题、填空题、编程题等题型，支持单选/多选/判断
- **LLM 智能解答** — 调用 DeepSeek（兼容 OpenAI 接口）生成答案
- **自动填答** — 选择/填空题自动填入页面
- **编程题手动模式** — 编程题打印答案，由用户手动填入
- **登录态持久化** — 通过 `auth.json` 保存浏览器登录状态，无需重复登录

## 项目结构

```
.
├── main.py              # 主入口，命令行交互式答题
├── config.py            # 配置文件（LLM、浏览器、答题参数）
├── requirements.txt     # Python 依赖
├── core/
│   ├── parser.py        # 题目解析（从页面提取题干、选项、题型）
│   ├── solver.py        # LLM 求解器（调用 API 生成答案）
│   └── answer.py        # 答案填入与翻页提交
├── scripts/
│   ├── login.py         # 首次登录，保存 auth.json
│   ├── auto_answer.py   # 备用答题脚本
│   ├── fill_only.py     # 纯填答模式
│   └── save_page.py     # 保存页面 HTML 用于调试
├── utils/
│   └── logger.py        # 统一日志输出
└── debug/               # 调试用页面快照
```

## 快速开始

### 1. 环境准备

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置

编辑 `config.py`，填入 LLM API 信息：

```python
LLM_API_BASE = "https://api.deepseek.com/v1"
LLM_API_KEY = "your-api-key-here"
LLM_MODEL = "deepseek-chat"
```

### 3. 首次登录

```bash
python scripts/login.py
```

浏览器会自动打开云校园登录页，手动完成登录后，登录态会保存到 `auth.json`。

### 4. 开始答题

```bash
python main.py
```

进入答题页面后按回车，系统会自动逐页解析题目、调用 LLM 解答并填入答案。编程题会打印到终端，需要手动填入。

## 配置说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `HEADLESS` | 是否无头模式（调试建议 `False`） | `False` |
| `SLOW_MO` | 操作间隔毫秒，模拟人类速度 | `300` |
| `PAGE_TIMEOUT` | 页面加载超时（毫秒） | `30000` |
| `ANSWER_DELAY` | 每题作答延迟范围（秒） | `(1.0, 3.0)` |
| `MAX_RETRIES` | LLM 调用失败重试次数 | `3` |

## 依赖

- Python ≥ 3.9
- [Playwright](https://playwright.dev/) — 浏览器自动化
- [OpenAI SDK](https://github.com/openai/openai-python) — LLM API 调用
