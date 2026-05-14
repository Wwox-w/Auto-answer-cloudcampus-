"""
答案填充与提交模块
"""

import random
import time
from playwright.sync_api import Page
from config import Config
from utils.logger import info, warn, error


def fill_answers(page: Page, questions: list[dict], config: Config = None):
    """将解答填入页面对应的表单元素"""
    cfg = config or Config()
    total = len(questions)

    for i, q in enumerate(questions):
        qtype = q.get("type", "")
        info(f"[{i + 1}/{total}] 填入 #{q.get('number')} ({qtype})...")

        fill_funcs = {
            "multichoice": _fill_multichoice,
            "multichoice_multi": _fill_multichoice_multi,
            "truefalse": _fill_multichoice,  # 判断题复用单选逻辑
            "coderunner": _fill_coderunner,
            "shortanswer": _fill_shortanswer,
            "match": _fill_match,
        }

        filler = fill_funcs.get(qtype)
        if filler:
            try:
                filler(page, q)
            except Exception as e:
                error(f"填入 #{q.get('number')} 失败: {e}")
        else:
            warn(f"跳过未知题型 {qtype}")

        # 模拟人类作答延迟
        delay = random.uniform(*cfg.ANSWER_DELAY)
        time.sleep(delay)


def submit_page(page: Page) -> str:
    """
    提交当前页面。
    返回 "next"（还有下一页）、"finished"（全部完成）、"error"
    """
    # 查找提交/下一页按钮
    next_btn = page.query_selector(
        'input[type="submit"][name="next"], '
        'input[type="submit"][value*="Next"], '
        'button:has-text("Next")'
    )
    finish_btn = page.query_selector(
        'input[type="submit"][name="finish"], '
        'button:has-text("Submit all"), '
        'button:has-text("提交所有"), '
        'input[value*="Submit all"]'
    )

    if finish_btn:
        info("检测到「提交全部」按钮，执行最终提交")
        finish_btn.click()
        # 处理 Moodle 确认弹窗
        time.sleep(1)
        confirm_btn = page.query_selector(
            'button:has-text("Submit all and finish"), '
            'input[value*="Submit all and finish"]'
        )
        if confirm_btn:
            confirm_btn.click()
        page.wait_for_load_state("networkidle")
        return "finished"

    elif next_btn:
        info("点击「下一页」")
        next_btn.click()
        page.wait_for_load_state("networkidle")
        return "next"

    else:
        # 尝试寻找任何提交按钮
        any_submit = page.query_selector(
            'input[type="submit"], button[type="submit"], '
            'button:has-text("Submit"), button:has-text("提交")'
        )
        if any_submit:
            info("找到提交按钮，尝试提交")
            any_submit.click()
            page.wait_for_load_state("networkidle")
            return "finished"

        warn("未找到翻页/提交按钮，可能已是最后一页")
        return "finished"


# ====================================================================
# 各题型填充实现
# ====================================================================

def _fill_multichoice(page: Page, q: dict):
    """单选 / 判断 — 点击对应 radio"""
    answer = q.get("answer", "")
    if not answer:
        warn(f"#{q.get('number')} 无答案，跳过")
        return

    options = q.get("options", [])
    if not options:
        return

    # 找到匹配的 value（LLM 可能返回 value 或 label 文本）
    target_value = _match_option(answer, options)
    if not target_value:
        warn(f"#{q.get('number')} 无法匹配答案 '{answer}' 到选项")
        return

    name = options[0].get("name", "")
    selector = f'input[name="{name}"][value="{target_value}"]'
    try:
        page.check(selector)
    except Exception:
        # 回退：尝试点击 label
        try:
            page.click(f'label:has(input[value="{target_value}"])')
        except Exception:
            warn(f"选项选择失败: {selector}")


def _fill_multichoice_multi(page: Page, q: dict):
    """多选 — 点击多个 checkbox"""
    answers = q.get("answer", [])
    if not answers:
        warn(f"#{q.get('number')} 无答案，跳过")
        return

    options = q.get("options", [])
    if not options:
        return

    name = options[0].get("name", "")
    for ans in answers:
        target_value = _match_option(ans, options)
        if not target_value:
            warn(f"多选: 无法匹配 '{ans}'")
            continue
        try:
            page.check(f'input[name="{name}"][value="{target_value}"]')
        except Exception as e:
            warn(f"多选选项 {target_value} 失败: {e}")


def _fill_coderunner(page: Page, q: dict):
    """编程题 — 多策略填入 ACE 编辑器"""
    code = q.get("answer", "")
    answer_name = q.get("answerName", "")
    if not code or not answer_name:
        warn(f"#{q.get('number')} 无代码答案，跳过")
        return

    # 策略1: 通过 JS 操作 ACE 编辑器 API
    result = page.evaluate('''
        ({answerName, code}) => {
            const ta = document.querySelector(`textarea[name="${answerName}"]`);
            if (!ta) return "textarea_not_found";

            // 找 ACE 编辑器实例
            const aceId = ta.id ? ta.id.replace(/^id_/, "ace_") : "";
            const aceEl = aceId ? document.getElementById(aceId) : null;

            if (aceEl && window.ace) {
                try {
                    const editor = ace.edit(aceEl);
                    editor.setValue(code, -1);
                    editor.clearSelection();
                    // 同步到隐藏的 textarea
                    ta.value = code;
                    ta.dispatchEvent(new Event("change", {bubbles: true}));
                    ta.dispatchEvent(new Event("input", {bubbles: true}));
                    return "ace_ok";
                } catch(e) {
                    return "ace_error:" + e.message;
                }
            }

            // 无 ACE，直接设 textarea
            ta.value = code;
            ta.dispatchEvent(new Event("change", {bubbles: true}));
            ta.dispatchEvent(new Event("input", {bubbles: true}));
            return "textarea_ok";
        }
    ''', {"answerName": answer_name, "code": code})

    info(f"CodeRunner #{q.get('number')} 填入: {result}")

    # 策略2: 如果 JS 方式失败，用键盘模拟
    if "not_found" in result or "error" in result:
        warn(f"JS 填入失败({result})，尝试键盘模拟")
        try:
            # 点击 ACE 编辑器区域
            ace_selector = f'[id^="ace_"][id$="{answer_name.split(":")[-1]}"], .ace_editor'
            editor_el = page.query_selector(ace_selector)
            if editor_el:
                editor_el.click()
            else:
                # 点 textarea
                page.click(f'textarea[name="{answer_name}"]')

            # 全选删除
            page.keyboard.press("Meta+a")
            page.keyboard.press("Backspace")
            time.sleep(0.1)
            # 逐行输入
            for line in code.split("\n"):
                page.keyboard.type(line, delay=5)
                page.keyboard.press("Enter")
        except Exception as e:
            error(f"键盘模拟也失败: {e}")


def _fill_shortanswer(page: Page, q: dict):
    """填空题 — 模拟人工输入"""
    answer = q.get("answer", "")
    input_name = q.get("inputName", "")
    if not answer or not input_name:
        warn(f"#{q.get('number')} 无填空答案，跳过")
        return

    try:
        selector = f'input[name="{input_name}"]'
        # 先点击聚焦
        page.click(selector)
        # 全选清空
        page.keyboard.press("Meta+a")
        page.keyboard.press("Backspace")
        # 逐字符输入（模拟人工打字）
        page.type(selector, answer, delay=30)
    except Exception as e:
        warn(f"填空填入失败: {e}")


def _fill_match(page: Page, q: dict):
    """匹配题 — 选择下拉选项"""
    answer_map = q.get("answer", {})
    if not answer_map:
        warn(f"#{q.get('number')} 无匹配答案，跳过")
        return

    for select_name, value in answer_map.items():
        try:
            page.select_option(f'select[name="{select_name}"]', value)
        except Exception as e:
            warn(f"匹配选项 {select_name} 失败: {e}")


# ====================================================================
# 辅助：模糊匹配 LLM 答案到选项 value
# ====================================================================

def _match_option(answer: str, options: list[dict]) -> str | None:
    """
    LLM 可能返回 value、label 文本、选项字母(A/B/C)等。
    尝试多种策略匹配到正确的 value。
    """
    answer = answer.strip()

    # 1. 精确匹配 value
    for opt in options:
        if opt.get("value", "") == answer:
            return opt["value"]

    # 2. 精确匹配 label
    for opt in options:
        if opt.get("label", "").strip() == answer:
            return opt["value"]

    # 3. label 包含答案 或 答案包含 label
    for opt in options:
        label = opt.get("label", "").strip()
        if answer in label or label in answer:
            return opt["value"]

    # 4. 字母匹配 (A/B/C/D → 第 0/1/2/3 个选项)
    letter_map = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5}
    ans_lower = answer.lower().strip(".")
    if ans_lower in letter_map:
        idx = letter_map[ans_lower]
        if idx < len(options):
            return options[idx]["value"]

    # 5. 数字匹配 (0/1/2/3 → value 或 index)
    if answer.isdigit():
        idx = int(answer)
        # 先看是否有 value 等于这个数字
        for opt in options:
            if opt.get("value", "") == answer:
                return opt["value"]
        # 再按 index
        if idx < len(options):
            return options[idx]["value"]

    # 6. 模糊：取 label 开头匹配
    for opt in options:
        label = opt.get("label", "").strip().lower()
        if label.startswith(answer.lower()[:10]):
            return opt["value"]

    return None
