# Auto-Answer Web 前端设计说明书

## 概述

将现有的 CLI 答题助手改造为全功能 Web 应用。用户通过浏览器完成登录、配置、答题监控、历史查看全流程，后端驱动 Playwright + LLM 自动答题，前端通过 WebSocket 实时展示进度。

## 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 后端框架 | FastAPI (Python) | REST API + WebSocket |
| 浏览器自动化 | Playwright (后台线程) | 解析 + 填答 |
| LLM | OpenAI SDK (DeepSeek 兼容) | 生成答案 |
| 前端框架 | Vue 3 + TypeScript | Composition API |
| 构建工具 | Vite | 快速 HMR |
| 样式 | Tailwind CSS | 原子化 CSS |
| 设计系统 | shadcn/ui (Radix + Tailwind) | 现代 SaaS 风格组件 |
| 实时通信 | WebSocket | 答题进度流式推送 |
| 状态管理 | Pinia | Vue 3 官方推荐 |

## 架构

```
前端 (Vue 3 + Vite)          后端 (FastAPI)              引擎层
┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐
│ Dashboard        │────▶│ REST /api/config  │     │              │
│ Session          │◀────│ REST /api/history │     │ AnswerEngine │
│ Config           │     │ REST /api/login   │────▶│ · Playwright │
│ History          │◀══╡│ WebSocket         │     │ · Solver     │
│                  │     │ /ws/progress      │     │ · Filler     │
└─────────────────┘     └──────────────────┘     └──────────────┘
                                │
                                ▼
                        ┌──────────────┐
                        │ File Storage │
                        │ · auth.json  │
                        │ · config.json│
                        │ · history/   │
                        └──────────────┘
```

- **REST API**：配置 CRUD、历史查询、登录触发
- **WebSocket**：答题进度实时推送（每题解析 → LLM解答 → 填入 → 翻页）
- **AnswerEngine**：在后台线程中运行，封装 Playwright + Solver + Filler，通过回调向 WebSocket 推送状态
- **前端路由**：4 个页面 (`/dashboard`, `/session`, `/config`, `/history`)

## 页面设计

### 1. Dashboard (`/dashboard`)

首页，用户进入后看到：

- **状态卡片**（3 个）：LLM 模型状态、登录状态、答题就绪状态
- **开始答题按钮**：primary CTA，点击跳转到 `/session` 并触发答题流程
- **近期历史**：右侧栏显示最近 3 条答题记录摘要

### 2. Session (`/session`) — 核心页面

实时答题面板，左右分栏：

- **左侧 - 题目清单**：当前页所有题目，每道题显示类型、编号、状态图标（等待/解答中/已填/失败）
- **右侧 - 当前题详情**：题干文本、LLM 生成的答案、实时操作日志流
- **顶栏**：当前页码、页数进度、"停止"按钮（随时中断）
- **编程题特殊处理**：答案展示但不自动填入，弹出提示用户手动操作
- **WebSocket 状态**：连接状态指示器，断线自动重连

### 3. Config (`/config`)

配置管理页面：

- **LLM 配置**：API Base URL、API Key（掩码显示）、模型选择
- **浏览器配置**：无头模式开关、操作延迟范围、页面超时
- **保存按钮**：持久化到 `config.json`

### 4. History (`/history`)

历史记录列表：

- 每条记录显示：日期时间、题目总数、页数、正确率（预估）
- 点击「查看详情」展开每题问答记录

## 数据流

### 答题流程

```
用户点击"开始答题"
  → POST /api/session/start
    → AnswerEngine 启动（后台线程）
      → Playwright 打开浏览器
      → 导航到答题页
      → WebSocket 推送: { event: "page_start", page: 1 }
      → 循环每道题：
          解析 → WebSocket: { event: "question_parsed" }
          LLM 解答 → WebSocket: { event: "answer_generated" }
          填入 → WebSocket: { event: "answer_filled" }
      翻页 → WebSocket: { event: "page_complete" }
      继续或结束 → WebSocket: { event: "session_end" }
```

### WebSocket 消息格式

```json
{
  "event": "answer_generated",
  "question_number": 3,
  "type": "multichoice",
  "text": "TCP协议中...",
  "answer": "2",
  "status": "filled"
}
```

## 错误处理

- **LLM 调用失败**：前端显示 retry 按钮，后端指数退避重试最多 3 次
- **WebSocket 断线**：前端自动重连，重连后拉取当前进度快照
- **Playwright 超时**：前端显示超时警告，允许用户手动干预
- **未登录**：Dashboard 状态卡片显示"未登录"，引导用户登录

## 文件结构（新增）

```
frontend/                    # Vue 3 前端
├── src/
│   ├── App.vue
│   ├── main.ts
│   ├── router/index.ts
│   ├── stores/              # Pinia
│   │   ├── session.ts       # 答题会话状态
│   │   └── config.ts        # 配置状态
│   ├── views/
│   │   ├── Dashboard.vue
│   │   ├── Session.vue
│   │   ├── Config.vue
│   │   └── History.vue
│   ├── components/
│   │   ├── StatusCard.vue
│   │   ├── QuestionList.vue
│   │   ├── QuestionDetail.vue
│   │   ├── LogStream.vue
│   │   └── NavBar.vue
│   └── composables/
│       └── useWebSocket.ts
├── package.json
├── vite.config.ts
└── tailwind.config.js

backend/                     # FastAPI 后端
├── main.py                  # FastAPI app 入口
├── routes/
│   ├── config.py
│   ├── session.py
│   └── history.py
├── engine/
│   └── answer_engine.py     # 答题引擎（重构自 core/）
├── ws/
│   └── progress.py          # WebSocket 管理
└── storage.py               # JSON 文件存储
```

## 设计风格

- **风格**：现代 SaaS（Linear / Vercel 风格）
- **配色**：深色主题为主，灰色底 + 柔和阴影 + 蓝色强调
- **组件**：shadcn/ui（Radix UI + Tailwind），圆角卡片、细腻边框
- **字体**：系统等宽/无衬线字体栈
- **实施时**：调用 `frontend-design` + `ui-ux-pro-max` skill 确保视觉品质
