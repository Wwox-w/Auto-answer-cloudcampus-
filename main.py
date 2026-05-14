#!/usr/bin/env python3
"""
答题系统 — 命令行入口
用法: python main.py
"""

import os
import time
from playwright.sync_api import sync_playwright
from config import Config
from core.parser import parse_questions
from core.solver import Solver
from core.answer import fill_answers, submit_page
from utils.logger import info, warn, error


def main():
    config = Config()

    if not os.path.exists("auth.json"):
        print("未找到 auth.json，请先运行: python scripts/login.py")
        return

    solver = Solver(config)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=config.HEADLESS, slow_mo=config.SLOW_MO)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()
        page.set_default_timeout(config.PAGE_TIMEOUT)

        page.goto("https://www.cloudcampus.com.cn/")
        info("浏览器已打开，请在浏览器中进入答题页面")

        input("\n>>> 进入答题页后，按回车开始自动答题...")

        for page_idx in range(20):
            info(f"\n{'='*50}")
            info(f"第 {page_idx + 1} 页：解析题目...")

            # 续期 cookie
            context.storage_state(path="auth.json")

            questions = parse_questions(page)
            if not questions:
                info("没有题目，答题结束")
                break

            info(f"共 {len(questions)} 道题: {[q['type'] for q in questions]}")

            # LLM 解答
            for q in questions:
                try:
                    q["answer"] = solver.solve(q)
                    ans_preview = str(q["answer"])[:80].replace("\n", " ")
                    info(f"  #{q['number']} [{q['type']}] → {ans_preview}")
                except Exception as e:
                    error(f"  #{q['number']} 解答失败: {e}")

            # 区分编程题和其他题
            code_qs = [q for q in questions if q.get("type") == "coderunner"]
            other_qs = [q for q in questions if q.get("type") != "coderunner"]

            # 自动填入选择/填空题
            if other_qs:
                info(f"自动填入 {len(other_qs)} 道选择/填空题...")
                fill_answers(page, other_qs, config)
                info("✓ 已填入")

            # 编程题：打印答案，等用户手动填
            if code_qs:
                print(f"\n{'─'*50}")
                print(f"本页有 {len(code_qs)} 道编程题，请手动填入以下答案：")
                for q in code_qs:
                    print(f"\n【第 {q['number']} 题】{q['text'][:100]}")
                    print("─ 答案 ─")
                    print(q.get("answer", "（无答案）"))
                    print("─────")
                input("\n>>> 手动填完编程题后，按回车继续...")

            # 翻页
            info("翻页...")
            result = submit_page(page)
            if result != "next":
                info("全部完成！请在浏览器中手动提交。")
                input("\n>>> 按回车退出...")
                break

            time.sleep(0.5)

        context.storage_state(path="auth.json")
        browser.close()


if __name__ == "__main__":
    main()
