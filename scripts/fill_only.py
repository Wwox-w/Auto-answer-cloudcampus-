#!/usr/bin/env python3
"""
只填答案，不提交 —— 填写完成后自己检查再手动点提交
"""

import sys
from playwright.sync_api import sync_playwright
from config import Config
from core.parser import parse_questions
from core.solver import Solver
from core.answer import fill_answers
from utils.logger import info, warn


def main():
    config = Config()

    if not config.LLM_API_KEY:
        print("请先在 config.py 中配置 LLM_API_KEY")
        sys.exit(1)

    quiz_url = input("请输入答题页面 URL: ").strip()
    if not quiz_url:
        sys.exit(1)

    solver = Solver(config)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config.HEADLESS, slow_mo=config.SLOW_MO)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()
        page.set_default_timeout(config.PAGE_TIMEOUT)

        info(f"打开: {quiz_url}")
        page.goto(quiz_url)
        page.wait_for_load_state("networkidle")

        # 如果是 view.php，点「开始答题」
        start_btn = page.query_selector(
            'button:has-text("Attempt quiz"), '
            'input[value*="Attempt quiz"], '
            'button:has-text("开始答题")'
        )
        if start_btn:
            info("点击「开始答题」")
            start_btn.click()
            page.wait_for_load_state("networkidle")

        page_num = 0
        while True:
            info(f"\n===== 第 {page_num + 1} 页 =====")

            questions = parse_questions(page)
            if not questions:
                # 检查是否已经是总结页
                if page.query_selector(".quizattemptsummary, .result-table"):
                    info("已是结果页，无需再答")
                else:
                    warn("未找到题目")
                break

            # 展示题目
            print(f"\n共 {len(questions)} 道题:")
            for q in questions:
                print(f"  #{q['number']} [{q['type']}] {q['text'][:60]}...")

            # LLM 求解
            print("\n解答中...\n")
            for q in questions:
                try:
                    q["answer"] = solver.solve(q)
                    preview = str(q["answer"])[:80].replace("\n", "\\n")
                    print(f"  #{q['number']} → {preview}")
                except Exception as e:
                    warn(f"  #{q['number']} 求解失败: {e}")

            # 填入页面
            fill_answers(page, questions, config)
            info("本页答案已填入，请检查后手动点击提交/下一页")

            # 等待用户手动操作
            input("\n翻到下一页后按回车继续...")
            page_num += 1

        print("\n全部处理完毕")
        browser.close()


if __name__ == "__main__":
    main()
