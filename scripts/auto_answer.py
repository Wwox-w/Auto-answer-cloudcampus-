#!/usr/bin/env python3
"""
自动答题主脚本

用法:
    python auto_answer.py

流程:
    1. 输入答题页面 URL
    2. 自动解析题目（支持选择、编程、判断、填空、匹配题）
    3. LLM 生成答案
    4. 填入并提交流程
"""

import sys
from playwright.sync_api import sync_playwright
from config import Config
from core.parser import parse_questions
from core.solver import Solver
from core.answer import fill_answers, submit_page
from utils.logger import info, warn, error


def main():
    config = Config()

    # ================================================================
    # 0. 检查配置
    # ================================================================
    if not config.LLM_API_KEY:
        print("⚠️  未配置 LLM_API_KEY，请在 config.py 中填入 API Key")
        print("   DeepSeek 注册地址: https://platform.deepseek.com")
        print("   (也支持 OpenAI / Ollama 等兼容接口)\n")
        use_local = input("是否在无 AI 模式下继续（仅解析题目，不答题）？[y/N]: ")
        if use_local.lower() != "y":
            sys.exit(0)

    # ================================================================
    # 1. 获取答题 URL
    # ================================================================
    print("\n" + "=" * 60)
    quiz_url = input("请输入答题页面 URL: ").strip()
    if not quiz_url:
        print("未输入 URL，退出")
        sys.exit(1)

    # 自动纠正 review.php → attempt.php
    if "review.php" in quiz_url:
        warn("检测到 review.php（回顾页），这是已提交的答题，无法再作答")
        print("请从课程页面重新进入答题，获取新的 attempt.php 链接")
        sys.exit(1)

    if "view.php" in quiz_url:
        info("检测到 view.php（测验首页），将自动点击「开始答题」按钮")

    # ================================================================
    # 2. 启动浏览器
    # ================================================================
    info("启动浏览器...")
    solver = Solver(config) if config.LLM_API_KEY else None

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO
        )
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()
        page.set_default_timeout(config.PAGE_TIMEOUT)

        # 导航到答题页
        info(f"打开: {quiz_url}")
        page.goto(quiz_url)
        page.wait_for_load_state("networkidle")

        # ================================================================
        # 3. 处理测验入口（view.php → 点击 "Attempt quiz"）
        # ================================================================
        start_btn = page.query_selector(
            'button:has-text("Attempt quiz"), '
            'input[value*="Attempt quiz"], '
            'button:has-text("开始答题"), '
            'a:has-text("Attempt quiz")'
        )
        if start_btn:
            info("点击「开始答题」按钮...")
            start_btn.click()
            page.wait_for_load_state("networkidle")

        # ================================================================
        # 4. 逐页答题
        # ================================================================
        page_num = 0

        while True:
            info(f"\n{'=' * 40}\n第 {page_num + 1} 页\n{'=' * 40}")

            # --- 计时器检测 ---
            timer = page.query_selector(".quiz-timer, #quiz-timer, .timeleft")
            if timer:
                remaining = timer.inner_text().strip()
                info(f"⏱ 剩余时间: {remaining}")

            # --- 解析题目 ---
            questions = parse_questions(page)

            if not questions:
                warn("当前页面未解析到题目")
                # 可能已经提交完成跳转到总结页
                summary = page.query_selector(".quizattemptsummary, .result-table")
                if summary:
                    info("检测到答题结果页，流程结束")
                break

            # --- 显示题目概览 ---
            print(f"\n📋 共 {len(questions)} 道题目:")
            for q in questions:
                qtype = q["type"]
                qtext = q["text"][:60].replace("\n", " ")
                print(f"  #{q['number']} [{qtype}] {qtext}...")

            # --- 求解 ---
            if solver:
                print("\n🤖 LLM 解答中...\n")
                for q in questions:
                    try:
                        q["answer"] = solver.solve(q)
                        ans_preview = str(q["answer"])[:80].replace("\n", "\\n")
                        print(f"  #{q['number']} → {ans_preview}")
                    except Exception as e:
                        error(f"  #{q['number']} 求解失败: {e}")
                        q["answer"] = ""
            else:
                print("\n⚠️ 无 LLM 模式，仅展示题目")

            # --- 确认（可选） ---
            if config.CONFIRM_BEFORE_SUBMIT and solver:
                confirm = input("\n是否填入并提交本页？[Y/n]: ").strip().lower()
                if confirm == "n":
                    info("用户取消，跳过本页")
                    page_num += 1
                    continue

            # --- 填入答案 ---
            if solver:
                fill_answers(page, questions, config)

            # --- 提交/翻页 ---
            result = submit_page(page)

            if result == "finished":
                info("全部答题完成！")
                break
            elif result == "next":
                page_num += 1
            else:
                warn(f"未知翻页状态: {result}")
                break

        # ================================================================
        # 5. 完成
        # ================================================================
        print("\n" + "=" * 60)
        print("答题流程结束")
        print("=" * 60)
        browser.close()


if __name__ == "__main__":
    main()
