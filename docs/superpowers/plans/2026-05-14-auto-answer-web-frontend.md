# Auto-Answer Web 前端实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 CLI 答题助手改造为全功能 Web 应用，用户通过浏览器完成配置、答题监控、历史查看。

**Architecture:** FastAPI 提供 REST API + WebSocket，Vue 3 前端实时展示答题进度。AnswerEngine 在后台线程驱动 Playwright + LLM，通过 WebSocket 推送每题状态。前端使用 shadcn-vue (Radix Vue + Tailwind) 现代 SaaS 暗色主题。

**Tech Stack:** Vue 3 + TypeScript + Vite + Tailwind CSS + shadcn-vue + Pinia | FastAPI + WebSocket + Playwright + OpenAI SDK

---

## Phase 1: 项目脚手架

### Task 1: 创建 Vue 3 前端项目骨架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.app.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/style.css`

- [ ] **Step 1: 初始化 Vite + Vue 3 + TypeScript 项目**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
npm create vite@latest frontend -- --template vue-ts
cd frontend && npm install
```

Expected: `frontend/` 目录创建成功，包含 Vite + Vue 3 + TS 基础文件。

- [ ] **Step 2: 安装前端依赖**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer/frontend
npm install vue-router@4 pinia
npm install -D tailwindcss @tailwindcss/vite postcss autoprefixer
npm install -D @types/node
```

- [ ] **Step 3: 安装 shadcn-vue 相关依赖**

shadcn-vue 需要 Radix Vue 原语 + 工具库：

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer/frontend
npm install radix-vue class-variance-authority clsx tailwind-merge
npm install lucide-vue-next
npm install -D tailwindcss-animate
```

- [ ] **Step 4: 配置 Vite (vite.config.ts)**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true }
    }
  }
})
```

- [ ] **Step 5: 配置 Tailwind + CSS (tailwind.config.js)**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
```

- [ ] **Step 6: 配置 CSS 变量 (src/style.css)**

```css
@import 'tailwindcss';

@layer base {
  :root {
    --background: 222 47% 6%;
    --foreground: 210 40% 98%;

    --card: 217 33% 12%;
    --card-foreground: 210 40% 98%;

    --popover: 217 33% 12%;
    --popover-foreground: 210 40% 98%;

    --primary: 217 91% 60%;
    --primary-foreground: 222 47% 6%;

    --secondary: 217 33% 17%;
    --secondary-foreground: 210 40% 98%;

    --muted: 217 33% 17%;
    --muted-foreground: 215 20% 60%;

    --accent: 217 33% 17%;
    --accent-foreground: 210 40% 98%;

    --destructive: 0 63% 31%;
    --destructive-foreground: 210 40% 98%;

    --border: 217 33% 20%;
    --input: 217 33% 20%;
    --ring: 217 91% 60%;

    --radius: 0.5rem;
  }
}
```

- [ ] **Step 7: 配置 App.vue 入口**

```vue
<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-background text-foreground antialiased">
    <RouterView />
  </div>
</template>
```

- [ ] **Step 8: 配置 main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 9: 验证前端能启动**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer/frontend
npx vite --host 2>&1 | head -10
```

Expected: Vite dev server 启动，无报错。

- [ ] **Step 10: Commit**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
git add frontend/
git commit -m "feat: 创建 Vue 3 + Vite + Tailwind 前端项目骨架"
```

---

### Task 2: 创建 FastAPI 后端项目结构

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/routes/__init__.py`
- Create: `backend/routes/config.py`
- Create: `backend/routes/session.py`
- Create: `backend/routes/history.py`
- Create: `backend/engine/__init__.py`
- Create: `backend/engine/answer_engine.py`
- Create: `backend/ws/__init__.py`
- Create: `backend/ws/progress.py`
- Create: `backend/storage.py`
- Modify: `config.py` (项目根目录，已有)

- [ ] **Step 1: 安装后端 Python 依赖**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
source venv/bin/activate
pip install fastapi uvicorn websockets
```

- [ ] **Step 2: 创建 backend/requirements.txt**

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
websockets>=13.0
playwright>=1.40.0
openai>=1.0.0
```

- [ ] **Step 3: 创建 backend/main.py — FastAPI 入口**

```python
"""Auto-Answer Web 后端入口"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.config import router as config_router
from backend.routes.session import router as session_router
from backend.routes.history import router as history_router

app = FastAPI(title="Auto-Answer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config_router, prefix="/api")
app.include_router(session_router, prefix="/api")
app.include_router(history_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 4: 创建路由占位文件**

Create `backend/routes/__init__.py` (空文件)

Create `backend/routes/config.py`:

```python
"""配置管理 API"""
from fastapi import APIRouter

router = APIRouter(tags=["config"])

@router.get("/config")
async def get_config():
    return {}

@router.put("/config")
async def update_config(data: dict):
    return {"status": "saved"}
```

Create `backend/routes/session.py`:

```python
"""答题会话 API"""
from fastapi import APIRouter

router = APIRouter(tags=["session"])

@router.post("/session/start")
async def start_session():
    return {"status": "started"}

@router.post("/session/stop")
async def stop_session():
    return {"status": "stopped"}
```

Create `backend/routes/history.py`:

```python
"""答题历史 API"""
from fastapi import APIRouter

router = APIRouter(tags=["history"])

@router.get("/history")
async def list_history():
    return []

@router.get("/history/{session_id}")
async def get_history_detail(session_id: str):
    return {}
```

Create `backend/engine/__init__.py` (空文件)

Create `backend/ws/__init__.py` (空文件)

- [ ] **Step 5: 验证后端能启动**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
source venv/bin/activate
cd backend && python -c "from main import app; print('OK')"
```

Expected: 打印 `OK`，无报错。

- [ ] **Step 6: Commit**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
git add backend/ config.py
git commit -m "feat: 创建 FastAPI 后端项目骨架和路由占位"
```

---

## Phase 2: 后端核心实现

### Task 3: 实现 storage.py — JSON 文件存储层

**Files:**
- Create: `backend/storage.py`

- [ ] **Step 1: 实现 storage.py**

```python
"""本地 JSON 文件存储"""
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
AUTH_FILE = BASE_DIR / "auth.json"
HISTORY_DIR = BASE_DIR / "history"
HISTORY_DIR.mkdir(exist_ok=True)


def read_config() -> dict:
    """读取配置，文件不存在返回默认值"""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {
        "llm_api_base": "https://api.deepseek.com/v1",
        "llm_api_key": "",
        "llm_model": "deepseek-chat",
        "headless": False,
        "slow_mo": 300,
        "page_timeout": 30000,
        "answer_delay": [1.0, 3.0],
        "max_retries": 3,
    }


def write_config(data: dict) -> None:
    """保存配置"""
    CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def check_auth() -> bool:
    """检查是否已登录"""
    return AUTH_FILE.exists()


def list_history(limit: int = 20) -> list[dict]:
    """列出最近的答题记录"""
    files = sorted(HISTORY_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    results = []
    for f in files[:limit]:
        try:
            d = json.loads(f.read_text())
            results.append({
                "id": f.stem,
                "date": d.get("date", ""),
                "total_questions": d.get("total_questions", 0),
                "pages": d.get("pages", 0),
                "model": d.get("model", ""),
            })
        except json.JSONDecodeError:
            pass
    return results


def get_history_detail(session_id: str) -> dict | None:
    """获取某次答题的详细记录"""
    f = HISTORY_DIR / f"{session_id}.json"
    if f.exists():
        return json.loads(f.read_text())
    return None


def save_history(session_id: str, data: dict) -> None:
    """保存答题记录"""
    f = HISTORY_DIR / f"{session_id}.json"
    f.write_text(json.dumps(data, indent=2, ensure_ascii=False))
```

- [ ] **Step 2: 运行 Python 验证**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
source venv/bin/activate
python -c "from backend.storage import read_config; print(read_config())"
```

Expected: 打印默认配置字典。

- [ ] **Step 3: Commit**

```bash
git add backend/storage.py
git commit -m "feat: 实现 JSON 文件存储层"
```

---

### Task 4: 实现 Config API 路由

**Files:**
- Modify: `backend/routes/config.py`

- [ ] **Step 1: 重写 config.py 路由**

```python
"""配置管理 API"""
from fastapi import APIRouter
from pydantic import BaseModel
from backend.storage import read_config, write_config, check_auth

router = APIRouter(tags=["config"])


class LLMConfig(BaseModel):
    llm_api_base: str = "https://api.deepseek.com/v1"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"


class BrowserConfig(BaseModel):
    headless: bool = False
    slow_mo: int = 300
    page_timeout: int = 30000


class AnswerConfig(BaseModel):
    answer_delay: list[float] = [1.0, 3.0]
    max_retries: int = 3


class FullConfig(BaseModel):
    llm: LLMConfig = LLMConfig()
    browser: BrowserConfig = BrowserConfig()
    answer: AnswerConfig = AnswerConfig()


@router.get("/config")
async def get_config():
    data = read_config()
    llm = LLMConfig(
        llm_api_base=data.get("llm_api_base", "https://api.deepseek.com/v1"),
        llm_api_key=data.get("llm_api_key", ""),
        llm_model=data.get("llm_model", "deepseek-chat"),
    )
    browser = BrowserConfig(
        headless=data.get("headless", False),
        slow_mo=data.get("slow_mo", 300),
        page_timeout=data.get("page_timeout", 30000),
    )
    answer = AnswerConfig(
        answer_delay=data.get("answer_delay", [1.0, 3.0]),
        max_retries=data.get("max_retries", 3),
    )
    return {
        "llm": llm.model_dump(),
        "browser": browser.model_dump(),
        "answer": answer.model_dump(),
        "has_auth": check_auth(),
    }


@router.put("/config")
async def update_config(config: FullConfig):
    data = {
        **config.llm.model_dump(),
        **config.browser.model_dump(),
        **config.answer.model_dump(),
    }
    write_config(data)
    return {"status": "saved"}
```

- [ ] **Step 2: 测试 API**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
sleep 2
curl -s http://localhost:8000/api/config | python -m json.tool
kill %1
```

Expected: 返回包含 llm/browser/answer/has_auth 的 JSON。

- [ ] **Step 3: Commit**

```bash
git add backend/routes/config.py
git commit -m "feat: 实现配置 CRUD API"
```

---

### Task 5: 实现 History API 路由

**Files:**
- Modify: `backend/routes/history.py`

- [ ] **Step 1: 重写 history.py 路由**

```python
"""答题历史 API"""
from fastapi import APIRouter, HTTPException
from backend.storage import list_history, get_history_detail

router = APIRouter(tags=["history"])


@router.get("/history")
async def get_history(limit: int = 20):
    return list_history(limit)


@router.get("/history/{session_id}")
async def get_history_item(session_id: str):
    detail = get_history_detail(session_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    return detail
```

- [ ] **Step 2: 测试 API**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
sleep 2
curl -s http://localhost:8000/api/history
curl -s http://localhost:8000/api/history/nonexistent
kill %1
```

Expected: `/api/history` 返回空数组 `[]`，`nonexistent` 返回 404。

- [ ] **Step 3: Commit**

```bash
git add backend/routes/history.py
git commit -m "feat: 实现答题历史 API"
```

---

### Task 6: 实现 AnswerEngine — 答题引擎（重构自 core/）

**Files:**
- Create: `backend/engine/answer_engine.py`

- [ ] **Step 1: 实现 answer_engine.py**

```python
"""答题引擎 — 在后台线程中驱动 Playwright + LLM 自动答题"""
import json
import os
import sys
import threading
import time
import random
from datetime import datetime
from typing import Callable

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from playwright.sync_api import sync_playwright
from core.parser import parse_questions
from core.solver import Solver
from core.answer import fill_answers, submit_page
from backend.storage import save_history


class AnswerEngine:
    """后台答题引擎，封装完整答题流程"""

    def __init__(self, config: dict, on_event: Callable[[dict], None]):
        self.config = config
        self.on_event = on_event  # 回调，向 WebSocket 推送事件
        self._thread: threading.Thread | None = None
        self._stop_flag = threading.Event()

    def start(self):
        """在后台线程启动答题"""
        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """停止答题"""
        self._stop_flag.set()

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _emit(self, event: str, **data):
        self.on_event({"event": event, **data})

    def _run(self):
        class _Cfg:
            def __init__(self, d):
                self.__dict__.update(d)

        cfg = _Cfg(self.config)

        if not os.path.exists("auth.json"):
            self._emit("error", message="未找到 auth.json，请先登录")
            return

        solver = Solver(cfg)
        session_questions = []
        page_count = 0

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(
                    headless=cfg.headless, slow_mo=cfg.slow_mo
                )
                context = browser.new_context(storage_state="auth.json")
                page = context.new_page()
                page.set_default_timeout(cfg.page_timeout)

                page.goto("https://www.cloudcampus.com.cn/")
                self._emit("ready", message="浏览器已打开，请进入答题页面")

                # 等待用户在浏览器中导航到答题页
                # Web 版：前端点击"开始答题"后通过 API 触发继续
                # 这里等待最多 60 秒或直到 flag 被 set
                waited = 0
                while not self._stop_flag.is_set() and waited < 120:
                    time.sleep(1)
                    waited += 1
                    # 检查是否已经在答题页面
                    has_questions = page.evaluate(
                        '() => document.querySelectorAll(".que").length > 0'
                    )
                    if has_questions:
                        break

                if self._stop_flag.is_set():
                    browser.close()
                    return

                for page_idx in range(20):
                    if self._stop_flag.is_set():
                        break

                    self._emit("page_start", page=page_idx + 1)

                    context.storage_state(path="auth.json")
                    questions = parse_questions(page)

                    if not questions:
                        self._emit("session_end", message="没有题目，答题结束")
                        break

                    page_count += 1
                    self._emit(
                        "questions_loaded",
                        page=page_idx + 1,
                        count=len(questions),
                        types=[q["type"] for q in questions],
                    )

                    for q in questions:
                        if self._stop_flag.is_set():
                            break
                        try:
                            self._emit(
                                "solving",
                                number=q["number"],
                                type=q["type"],
                                text=q.get("text", "")[:200],
                            )
                            q["answer"] = solver.solve(q)
                            ans_preview = str(q["answer"])[:200]
                            self._emit(
                                "answer_generated",
                                number=q["number"],
                                type=q["type"],
                                text=q.get("text", "")[:200],
                                answer=q["answer"],
                                preview=ans_preview,
                            )
                        except Exception as e:
                            self._emit(
                                "error",
                                number=q["number"],
                                message=f"解答失败: {e}",
                            )

                    code_qs = [
                        q for q in questions if q.get("type") == "coderunner"
                    ]
                    other_qs = [
                        q for q in questions if q.get("type") != "coderunner"
                    ]

                    if other_qs:
                        self._emit(
                            "filling",
                            count=len(other_qs),
                            message=f"自动填入 {len(other_qs)} 道选择/填空题",
                        )
                        fill_answers(page, other_qs, cfg)
                        for q in other_qs:
                            self._emit(
                                "filled",
                                number=q["number"],
                                type=q["type"],
                            )
                        session_questions.extend(other_qs)

                    if code_qs:
                        self._emit(
                            "code_required",
                            count=len(code_qs),
                            questions=[
                                {"number": q["number"], "text": q["text"][:200], "answer": q.get("answer", "")}
                                for q in code_qs
                            ],
                        )
                        # 等待用户手动填入编程题
                        # 前端确认后通过 API 继续
                        session_questions.extend(code_qs)

                    self._emit("submitting", page=page_idx + 1)
                    result = submit_page(page)
                    if result != "next":
                        self._emit("session_end", message="全部完成！")
                        break

                    time.sleep(0.5)

                context.storage_state(path="auth.json")
                browser.close()

        except Exception as e:
            self._emit("error", message=f"引擎异常: {e}")

        finally:
            # 保存历史记录
            session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
            save_history(
                session_id,
                {
                    "date": datetime.now().isoformat(),
                    "total_questions": len(session_questions),
                    "pages": page_count,
                    "model": self.config.get("llm_model", ""),
                    "questions": [
                        {
                            "number": q.get("number"),
                            "type": q.get("type"),
                            "text": q.get("text", "")[:200],
                            "answer": q.get("answer", ""),
                        }
                        for q in session_questions
                    ],
                },
            )
            self._emit("history_saved", session_id=session_id)
```

- [ ] **Step 2: 验证引擎导入无误**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
source venv/bin/activate
python -c "from backend.engine.answer_engine import AnswerEngine; print('OK')"
```

Expected: 打印 `OK`。

- [ ] **Step 3: Commit**

```bash
git add backend/engine/answer_engine.py
git commit -m "feat: 实现 AnswerEngine 后台答题引擎"
```

---

### Task 7: 实现 WebSocket 进度管理器 + Session API

**Files:**
- Create: `backend/ws/progress.py`
- Modify: `backend/routes/session.py`

- [ ] **Step 1: 实现 WebSocket 管理器 (ws/progress.py)**

```python
"""WebSocket 进度管理器"""
import asyncio
import json
from fastapi import WebSocket
from typing import Optional


class ProgressManager:
    """管理 WebSocket 连接，广播答题进度"""

    def __init__(self):
        self._connections: list[WebSocket] = []
        self._engine = None  # AnswerEngine 实例

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self._connections:
            self._connections.remove(ws)

    def set_engine(self, engine):
        self._engine = engine

    async def broadcast(self, event: dict):
        """向所有连接的 WebSocket 推送事件"""
        dead = []
        for ws in self._connections:
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.remove(ws)

    def create_callback(self):
        """创建同步回调函数，在线程安全的队列中推送事件"""
        loop = asyncio.get_event_loop()

        def on_event(event: dict):
            try:
                asyncio.run_coroutine_threadsafe(self.broadcast(event), loop)
            except Exception:
                pass

        return on_event

    def stop_engine(self):
        if self._engine and self._engine.running:
            self._engine.stop()


progress_manager = ProgressManager()
```

- [ ] **Step 2: 实现 Session API (routes/session.py)**

```python
"""答题会话 API"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.storage import read_config
from backend.ws.progress import progress_manager
from backend.engine.answer_engine import AnswerEngine

router = APIRouter(tags=["session"])

_engine: AnswerEngine | None = None


@router.post("/session/start")
async def start_session():
    global _engine
    config = read_config()
    _engine = AnswerEngine(config, progress_manager.create_callback())
    progress_manager.set_engine(_engine)
    _engine.start()
    return {"status": "started"}


@router.post("/session/stop")
async def stop_session():
    global _engine
    if _engine and _engine.running:
        _engine.stop()
    return {"status": "stopped"}


@router.websocket("/ws/progress")
async def ws_progress(ws: WebSocket):
    await progress_manager.connect(ws)
    try:
        while True:
            # 保持连接，接收客户端消息（如 heartbeat / confirm_code）
            data = await ws.receive_json()
            if data.get("type") == "heartbeat":
                await ws.send_json({"type": "heartbeat", "status": "alive"})
            elif data.get("type") == "confirm_code":
                # 用户确认已手动填入编程题
                await ws.send_json({"type": "code_confirmed"})
    except WebSocketDisconnect:
        progress_manager.disconnect(ws)
    except Exception:
        progress_manager.disconnect(ws)
```

- [ ] **Step 3: 注册 WebSocket 路由到 main.py**

Modify `backend/main.py`，添加 WebSocket endpoint:

```python
from backend.ws.progress import progress_manager

@app.websocket("/ws/progress")
async def ws_progress_endpoint(ws: WebSocket):
    await progress_manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "heartbeat":
                await ws.send_json({"type": "heartbeat", "status": "alive"})
            elif data.get("type") == "confirm_code":
                await ws.send_json({"type": "code_confirmed"})
    except Exception:
        progress_manager.disconnect(ws)
```

将 session.py 中的 WebSocket 路由移至 main.py 或保留在 session.py 但确保注册。

- [ ] **Step 4: 验证后端完整性**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
source venv/bin/activate
python -c "from backend.main import app; print('App OK, routes:', [r.path for r in app.routes])"
```

Expected: 列出所有路由，包含 `/api/config`, `/api/history`, `/api/session/start`, `/api/session/stop`, `/ws/progress`。

- [ ] **Step 5: Commit**

```bash
git add backend/ws/progress.py backend/routes/session.py backend/main.py
git commit -m "feat: 实现 WebSocket 进度管理和 Session API"
```

---

## Phase 3: 前端核心实现

### Task 8: 设置前端路由 + Pinia Store + 基础布局

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/stores/session.ts`
- Create: `frontend/src/stores/config.ts`
- Create: `frontend/src/composables/useWebSocket.ts`
- Create: `frontend/src/components/NavBar.vue`

- [ ] **Step 1: 实现路由 (router/index.ts)**

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
    { path: '/session', name: 'session', component: () => import('@/views/Session.vue') },
    { path: '/config', name: 'config', component: () => import('@/views/Config.vue') },
    { path: '/history', name: 'history', component: () => import('@/views/History.vue') },
  ],
})

export default router
```

- [ ] **Step 2: 实现 Session Store (stores/session.ts)**

```typescript
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface Question {
  number: number
  type: string
  text: string
  answer?: string
  status: 'waiting' | 'solving' | 'solved' | 'filled' | 'error'
}

export const useSessionStore = defineStore('session', () => {
  const running = ref(false)
  const currentPage = ref(0)
  const questions = ref<Question[]>([])
  const logs = ref<string[]>([])
  const codeQuestions = ref<Question[]>([])

  const currentQuestion = computed(() =>
    questions.value.find(q => q.status === 'solving') || questions.value[questions.value.length - 1]
  )

  function addLog(msg: string) {
    const time = new Date().toLocaleTimeString()
    logs.value.push(`[${time}] ${msg}`)
  }

  function reset() {
    running.value = false
    currentPage.value = 0
    questions.value = []
    logs.value = []
    codeQuestions.value = []
  }

  return { running, currentPage, questions, logs, codeQuestions, currentQuestion, addLog, reset }
})
```

- [ ] **Step 3: 实现 Config Store (stores/config.ts)**

```typescript
import { ref } from 'vue'
import { defineStore } from 'pinia'

export interface LLMConfig {
  llm_api_base: string
  llm_api_key: string
  llm_model: string
}

export interface BrowserConfig {
  headless: boolean
  slow_mo: number
  page_timeout: number
}

export const useConfigStore = defineStore('config', () => {
  const llm = ref<LLMConfig>({ llm_api_base: '', llm_api_key: '', llm_model: '' })
  const browser = ref<BrowserConfig>({ headless: false, slow_mo: 300, page_timeout: 30000 })
  const hasAuth = ref(false)
  const loading = ref(false)

  async function fetchConfig() {
    const res = await fetch('/api/config')
    const data = await res.json()
    llm.value = data.llm
    browser.value = data.browser
    hasAuth.value = data.has_auth
  }

  async function saveConfig() {
    loading.value = true
    await fetch('/api/config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ llm: llm.value, browser: browser.value, answer: {} }),
    })
    loading.value = false
  }

  return { llm, browser, hasAuth, loading, fetchConfig, saveConfig }
})
```

- [ ] **Step 4: 实现 useWebSocket composable (composables/useWebSocket.ts)**

```typescript
import { ref, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/session'

export function useWebSocket() {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const store = useSessionStore()

  function connect() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${location.host}/ws/progress`
    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      connected.value = true
      store.addLog('WebSocket 已连接')
    }

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleEvent(data)
    }

    ws.value.onclose = () => {
      connected.value = false
      store.addLog('WebSocket 已断开，3秒后重连...')
      setTimeout(connect, 3000)
    }

    ws.value.onerror = () => {
      connected.value = false
    }
  }

  function handleEvent(data: any) {
    switch (data.event) {
      case 'ready':
        store.addLog(data.message)
        break
      case 'page_start':
        store.currentPage = data.page
        store.addLog(`进入第 ${data.page} 页`)
        break
      case 'questions_loaded':
        store.addLog(`解析到 ${data.count} 道题`)
        break
      case 'solving':
        updateQuestion(data.number, { status: 'solving', text: data.text, type: data.type })
        store.addLog(`#${data.number} ${data.type} → LLM 求解中...`)
        break
      case 'answer_generated':
        updateQuestion(data.number, { status: 'solved', answer: data.preview, type: data.type })
        store.addLog(`#${data.number} ${data.type} → 答案已生成`)
        break
      case 'filling':
        store.addLog(data.message)
        break
      case 'filled':
        updateQuestion(data.number, { status: 'filled' })
        store.addLog(`#${data.number} ✓ 已填入`)
        break
      case 'code_required':
        store.codeQuestions = data.questions
        store.addLog(`有 ${data.count} 道编程题需要手动填入`)
        break
      case 'error':
        store.addLog(`❌ ${data.message || data.number + ' 出错'}`)
        if (data.number) updateQuestion(data.number, { status: 'error' })
        break
      case 'session_end':
        store.running = false
        store.addLog('答题结束')
        break
    }
  }

  function updateQuestion(number: number, updates: Partial<{ status: string; text: string; answer: string; type: string }>) {
    const q = store.questions.find(q => q.number === number)
    if (q) {
      Object.assign(q, updates)
    } else {
      store.questions.push({
        number,
        type: updates.type || 'unknown',
        text: updates.text || '',
        answer: updates.answer,
        status: (updates.status as any) || 'waiting',
      })
    }
  }

  function disconnect() {
    ws.value?.close()
  }

  onUnmounted(disconnect)

  return { connected, connect, disconnect }
}
```

- [ ] **Step 5: 实现 NavBar 组件 (components/NavBar.vue)**

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const links = [
  { path: '/', label: '仪表盘' },
  { path: '/session', label: '答题' },
  { path: '/config', label: '配置' },
  { path: '/history', label: '历史' },
]
</script>

<template>
  <nav class="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-primary font-bold text-lg">Auto-Answer</span>
      </div>
      <div class="flex items-center gap-1">
        <router-link
          v-for="link in links"
          :key="link.path"
          :to="link.path"
          class="px-3 py-1.5 rounded-md text-sm transition-colors"
          :class="route.path === link.path
            ? 'bg-primary/10 text-primary font-medium'
            : 'text-muted-foreground hover:text-foreground hover:bg-accent'"
        >
          {{ link.label }}
        </router-link>
      </div>
    </div>
  </nav>
</template>
```

- [ ] **Step 6: 验证前端编译通过**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer/frontend
npx vue-tsc --noEmit 2>&1 | head -20
```

Expected: 可能有些占位视图的导入报错（视图文件尚未创建），但 router/store/composable 自身无误。

- [ ] **Step 7: Commit**

```bash
git add frontend/src/router/ frontend/src/stores/ frontend/src/composables/ frontend/src/components/NavBar.vue
git commit -m "feat: 实现前端路由、Pinia Store、WebSocket composable、NavBar"
```

---

### Task 9: 实现 Dashboard 页面

**Files:**
- Create: `frontend/src/views/Dashboard.vue`
- Create: `frontend/src/components/StatusCard.vue`

**Design style:** 现代 SaaS 暗色主题（Linear/Vercel），shadcn-vue 组件，调用 `frontend-design` + `ui-ux-pro-max` skill 实现 UI。

- [ ] **Step 1: 使用 frontend-design + ui-ux-pro-max skill 设计并实现 Dashboard**

调用这两个 skill 完成 Dashboard 页面，设计规格：

```
页面布局：
┌─────────────────────────────────────────────┐
│  NavBar (固定顶栏)                            │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ 模型状态  │ │ 登录状态  │ │ 答题状态  │       │
│  │ ✓ 已配置  │ │ ✓ 已登录  │ │ 就绪     │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│                                             │
│  ┌───────────────────────────┐  ┌────────┐ │
│  │                           │  │ 最近记录 │ │
│  │     ▶ 开始答题            │  │ 05-14   │ │
│  │                           │  │ 05-13   │ │
│  └───────────────────────────┘  └────────┘ │
└─────────────────────────────────────────────┘
```

- 3 个 StatusCard 组件：模型状态、登录状态、答题状态
- 主 CTA "开始答题" 按钮，使用 primary 强调色
- 右侧近期历史列表（调用 /api/history）
- 页面 onMounted 时 fetchConfig 更新状态

关键代码结构（skill 实现时参考）：

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '@/stores/config'
import StatusCard from '@/components/StatusCard.vue'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const config = useConfigStore()

onMounted(() => config.fetchConfig())

function startSession() {
  router.push('/session')
}
</script>
```

- [ ] **Step 2: 验证 Dashboard 页面在前端可渲染**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer/frontend
npx vite --host &
sleep 3
curl -s http://localhost:5173 | head -20
kill %1
```

Expected: 返回 index.html，无编译错误。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Dashboard.vue frontend/src/components/StatusCard.vue
git commit -m "feat: 实现 Dashboard 首页"
```

---

### Task 10: 实现 Config 页面

**Files:**
- Create: `frontend/src/views/Config.vue`

**Design style:** 表单式配置页，shadcn-vue Input/Button/Switch 组件，调用 `frontend-design` + `ui-ux-pro-max` skill。

- [ ] **Step 1: 使用 frontend-design + ui-ux-pro-max skill 实现 Config 页面**

设计规格：

```
┌─────────────────────────────────────────────┐
│  ⚙️ 配置                                     │
│                                             │
│  LLM 配置                                    │
│  ┌─────────────────────────────────────┐    │
│  │ API Base URL  [https://api.deep...] │    │
│  │ API Key       [••••••••••••••••]    │    │
│  │ 模型           [dropdown]           │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  浏览器配置                                   │
│  ┌─────────────────────────────────────┐    │
│  │ 无头模式       [switch ○────●]       │    │
│  │ 操作延迟       1.0s ──●── 3.0s      │    │
│  │ 页面超时       30000 ms             │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌──────────┐                               │
│  │ 保存配置   │                               │
│  └──────────┘                               │
└─────────────────────────────────────────────┘
```

- 分组表单：LLM 配置 / 浏览器配置
- API Key 用 password 类型输入框，显示/隐藏切换
- 保存后 toast 提示成功
- onMounted 时加载已有配置

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/Config.vue
git commit -m "feat: 实现配置页面"
```

---

### Task 11: 实现 History 页面

**Files:**
- Create: `frontend/src/views/History.vue`

**Design style:** 列表+展开详情，shadcn-vue 组件，调用 `frontend-design` + `ui-ux-pro-max` skill。

- [ ] **Step 1: 使用 frontend-design + ui-ux-pro-max skill 实现 History 页面**

设计规格：

```
┌─────────────────────────────────────────────┐
│  📋 答题记录                                  │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ 05-14 14:20   15题 · 3页   查看详情▸ │    │
│  ├─────────────────────────────────────┤    │
│  │ #1 单选   ✓    #6 填空   ✓          │    │
│  │ #2 多选   ✓    #7 编程   ✓          │    │
│  │ ...                                 │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ 05-13 09:15   20题 · 4页   查看详情▸ │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

- 列表：每条记录显示日期、题数、页数
- 点击展开：显示该次答题的每道题和答案
- 空状态："暂无答题记录"
- onMounted 时 fetch /api/history

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/History.vue
git commit -m "feat: 实现历史记录页面"
```

---

### Task 12: 实现 Session 页面 — 核心实时答题面板

**Files:**
- Create: `frontend/src/views/Session.vue`
- Create: `frontend/src/components/QuestionList.vue`
- Create: `frontend/src/components/QuestionDetail.vue`
- Create: `frontend/src/components/LogStream.vue`

**Design style:** 实时答题流水线面板，深色主题 + 状态色彩编码，调用 `frontend-design` + `ui-ux-pro-max` skill。

- [ ] **Step 1: 使用 frontend-design + ui-ux-pro-max skill 实现 Session 页面**

设计规格（左右分栏）：

```
┌──────────────────────────────────────────────────────┐
│  ● 答题中  第 3/5 页                    [停止]        │
├──────────────┬───────────────────────────────────────┤
│ 题目清单      │ #3 填空题 ● 解答中                     │
│              │                                       │
│ #1 单选 ✓    │ TCP协议中建立连接需要___次握手...       │
│ #2 多选 ✓    │                                       │
│ #3 填空 ●    │ ┌─ LLM 已生成 ──────────────────────┐ │
│ #4 编程 ○    │ │ 三, 四                            │ │
│ #5 匹配 ○    │ └──────────────────────────────────┘ │
│              │                                       │
│              │ 实时日志                               │
│              │ [14:05:01] 解析到 5 道题               │
│              │ [14:05:02] #1 单选 → 答案已生成        │
│              │ [14:05:03] #1 ✓ 已填入                │
│              │ [14:05:04] #2 多选 → 答案已生成        │
└──────────────┴───────────────────────────────────────┘
```

关键交互：
- 左侧 QuestionList：每道题的状态图标（等待 ○ / 解答中 ● / 已填 ✓ / 失败 ✗），色彩编码
- 右侧当前题详情：题干文本 + LLM 答案展示区 + LogStream
- 顶栏：WebSocket 连接状态、页码进度、停止按钮
- 开始按钮（首次进入）：点击触发 POST /api/session/start + WebSocket connect
- 停止按钮：POST /api/session/stop，确认弹窗

Session.vue 核心逻辑：

```vue
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useWebSocket } from '@/composables/useWebSocket'
import NavBar from '@/components/NavBar.vue'
import QuestionList from '@/components/QuestionList.vue'
import QuestionDetail from '@/components/QuestionDetail.vue'
import LogStream from '@/components/LogStream.vue'

const router = useRouter()
const store = useSessionStore()
const { connected, connect, disconnect } = useWebSocket()

onMounted(() => {
  if (!store.running) {
    store.reset()
  }
})

async function startSession() {
  store.reset()
  store.running = true
  store.addLog('正在启动答题引擎...')
  await fetch('/api/session/start', { method: 'POST' })
  connect()
}

async function stopSession() {
  await fetch('/api/session/stop', { method: 'POST' })
  disconnect()
  store.running = false
  store.addLog('答题已停止')
}
</script>
```

- [ ] **Step 2: 验证前端编译通过**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer/frontend
npx vue-tsc --noEmit 2>&1 | tail -5
```

Expected: 无 TypeScript 错误。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Session.vue frontend/src/components/QuestionList.vue frontend/src/components/QuestionDetail.vue frontend/src/components/LogStream.vue
git commit -m "feat: 实现 Session 实时答题面板"
```

---

## Phase 4: 集成与收尾

### Task 13: 更新 requirements.txt 和启动脚本

**Files:**
- Modify: `requirements.txt`
- Create: `start.sh`

- [ ] **Step 1: 更新根目录 requirements.txt**

```
playwright>=1.40.0
openai>=1.0.0
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
websockets>=13.0
```

- [ ] **Step 2: 创建启动脚本 start.sh**

```bash
#!/bin/bash
set -e

cd "$(dirname "$0")"

# 启动后端
source venv/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 启动前端 dev server
cd frontend
npx vite --host &
FRONTEND_PID=$!
cd ..

echo "后端: http://localhost:8000"
echo "前端: http://localhost:5173"
echo "按 Ctrl+C 停止"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
```

```bash
chmod +x start.sh
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt start.sh
git commit -m "feat: 更新依赖和启动脚本"
```

---

### Task 14: 端到端验证

- [ ] **Step 1: 启动后端**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer
source venv/bin/activate
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 2
```

- [ ] **Step 2: 测试 API 端点**

```bash
# 健康检查
curl -s http://localhost:8000/api/health

# 配置 API
curl -s http://localhost:8000/api/config | python -m json.tool

# 历史 API
curl -s http://localhost:8000/api/history
```

Expected: 所有端点返回 200。

- [ ] **Step 3: 启动前端**

```bash
cd /Users/pwl/Desktop/NEFU/Auto-answer/frontend
npx vite --host &
sleep 3
```

- [ ] **Step 4: 验证前端页面**

```bash
# 检查页面可访问
curl -s http://localhost:5173 | grep -o '<title>.*</title>'
```

Expected: 返回 index.html 或 Vue SPA 标题。

- [ ] **Step 5: 验证前后端联通**

前端 dev server 配置了 proxy，`/api` 请求代理到 `localhost:8000`：

```bash
curl -s http://localhost:5173/api/health
```

Expected: `{"status":"ok"}`。

- [ ] **Step 6: 清理并 Commit**

```bash
kill %1 %2 2>/dev/null || true
git add -A
git commit -m "feat: 端到端验证，前后端联通"
```
