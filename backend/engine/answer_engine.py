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
                # 同时设置 lowercase 和 UPPERCASE 属性，兼容旧代码
                for k, v in d.items():
                    setattr(self, k, v)
                    setattr(self, k.upper(), v)

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

                # 自动检测登录表单并填入账号密码
                username = cfg.username or ""
                password = cfg.password or ""
                if username and password:
                    try:
                        # 等待登录表单出现
                        page.wait_for_selector(
                            'input[type="text"], input[name*="user"], input[name*="login"], '
                            'input[type="password"]',
                            timeout=5000
                        )
                        # 判断是否有密码框（登录页特征）
                        pwd_inputs = page.query_selector_all('input[type="password"]')
                        if pwd_inputs:
                            self._emit("ready", message="检测到登录页，正在自动登录...")
                            # 找用户名输入框
                            user_input = page.query_selector(
                                'input[type="text"], input[name*="user"], input[name*="login"], '
                                'input[name*="email"], input[name*="account"]'
                            )
                            if user_input:
                                user_input.fill(username)
                                time.sleep(0.3)
                            # 填密码
                            pwd_inputs[0].fill(password)
                            time.sleep(0.3)
                            # 找登录按钮
                            login_btn = page.query_selector(
                                'button[type="submit"], input[type="submit"], '
                                'button:has-text("登录"), button:has-text("登 录"), '
                                'button:has-text("Login"), button:has-text("Sign in")'
                            )
                            if login_btn:
                                login_btn.click()
                                page.wait_for_load_state("networkidle")
                                # 保存新登录态
                                context.storage_state(path="auth.json")
                                self._emit("ready", message="自动登录成功，请进入答题页面")
                            else:
                                self._emit("ready", message="已填入账号密码，请手动点击登录")
                        else:
                            self._emit("ready", message="浏览器已打开，请进入答题页面")
                    except Exception:
                        self._emit("ready", message="浏览器已打开，请进入答题页面")
                else:
                    self._emit("ready", message="浏览器已打开，请进入答题页面")

                # 等待用户在浏览器中导航到答题页
                waited = 0
                while not self._stop_flag.is_set() and waited < 300:
                    time.sleep(1)
                    waited += 1
                    try:
                        has_questions = page.evaluate(
                            '() => document.querySelectorAll(".que").length > 0'
                        )
                        if has_questions:
                            break
                    except Exception:
                        # 页面导航中，执行上下文暂时不可用，继续等待
                        pass

                if self._stop_flag.is_set():
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
                            usage = solver.get_usage()
                            self._emit(
                                "answer_generated",
                                number=q["number"],
                                type=q["type"],
                                text=q.get("text", "")[:200],
                                answer=q["answer"],
                                preview=ans_preview,
                                usage=usage,
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
                        session_questions.extend(code_qs)

                    self._emit("submitting", page=page_idx + 1)
                    result = submit_page(page)
                    if result != "next":
                        self._emit("session_end", message="全部完成！")
                        break

                    time.sleep(0.5)

                context.storage_state(path="auth.json")
                # 浏览器保持打开，用户可以手动检查答案

        except Exception as e:
            self._emit("error", message=f"引擎异常: {e}")

        finally:
            session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
            save_history(
                session_id,
                {
                    "status": "completed",
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
