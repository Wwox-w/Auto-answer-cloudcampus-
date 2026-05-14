"""
答案求解器 —— 调用 LLM 生成答案
"""

import json
import time
from openai import OpenAI
from config import Config
from utils.logger import info, warn, error


class Solver:
    """LLM 答案求解器"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.client = None
        if self.config.LLM_API_KEY:
            self.client = OpenAI(
                api_key=self.config.LLM_API_KEY,
                base_url=self.config.LLM_API_BASE
            )

    def solve(self, question: dict) -> str | dict:
        """根据题目类型调用对应求解方法"""
        qtype = question.get("type", "")

        handlers = {
            "multichoice": self._solve_multichoice,
            "multichoice_multi": self._solve_multichoice_multi,
            "truefalse": self._solve_truefalse,
            "coderunner": self._solve_coderunner,
            "shortanswer": self._solve_shortanswer,
            "match": self._solve_match,
        }

        handler = handlers.get(qtype)
        if handler:
            return handler(question)

        warn(f"未知题型 {qtype}，尝试通用求解")
        return self._solve_generic(question)

    # ================================================================
    # 各题型 Prompt 与求解
    # ================================================================

    def _solve_multichoice(self, q: dict) -> str:
        """单选题 → 返回选项 value"""
        options_text = self._format_options(q["options"])
        prompt = f"""你是一个答题助手。请回答以下单选题，只回复正确答案对应选项的 value 值。

题目：
{q['text']}

选项：
{options_text}

请只回复选项的 value 值（如 1、2、A、B 等），不要包含任何其他内容。"""
        return self._call_llm(prompt).strip()

    def _solve_multichoice_multi(self, q: dict) -> list[str]:
        """多选题 → 返回选项 value 列表"""
        options_text = self._format_options(q["options"])
        prompt = f"""你是一个答题助手。请回答以下多选题，回复所有正确答案对应选项的 value 值。

题目：
{q['text']}

选项：
{options_text}

请回复选项的 value 值，多个用逗号分隔（如 A,C,D）。"""
        raw = self._call_llm(prompt).strip()
        return [v.strip() for v in raw.replace("，", ",").split(",") if v.strip()]

    def _solve_truefalse(self, q: dict) -> str:
        """判断题 → 返回正确选项的 value"""
        options_text = self._format_options(q["options"])
        prompt = f"""你是一个答题助手。请判断以下说法的正误。

题目：
{q['text']}

选项：
{options_text}

请只回复正确选项的 value 值。"""
        return self._call_llm(prompt).strip()

    def _solve_coderunner(self, q: dict) -> str:
        """编程题 → 补全代码"""
        examples = q.get("examples", "")
        template = q.get("template", "")
        lang = q.get("language", "python3")

        if template:
            prompt = f"""你是一个编程高手。下面是代码填空题，已有模板代码，你需要补全函数体使其通过测试。

# 题目要求
{q['text']}

# 已有代码模板
```{lang}
{template}
```
"""
        else:
            prompt = f"""你是一个编程高手。请根据以下题目要求编写完整的 {lang} 代码。

# 题目要求
{q['text']}
"""

        if examples:
            prompt += f"""
# 示例
{examples}
"""

        if template:
            prompt += """
# 要求
- 保持已有的函数签名和结构不变
- 只补全函数体内部逻辑
- 输出完整的代码（包含已有的部分）
- 不要添加任何解释，只输出代码"""
        else:
            prompt += """
# 要求
- 输出完整可运行的代码
- 严格按照题目要求的函数名和参数
- 不要添加任何解释，只输出代码"""

        prompt += "\n\n请直接输出代码："

        code = self._call_llm(prompt).strip()
        if code.startswith("```"):
            lines = code.split("\n")
            code = "\n".join(lines[1:]) if len(lines) > 1 else code
            if code.endswith("```"):
                code = code[:-3].strip()
        return code

    def _solve_shortanswer(self, q: dict) -> str:
        """填空题 → 返回答案文本"""
        prompt = f"""你是一个答题助手。请回答以下填空题，只回复答案，不要包含任何解释。

题目：
{q['text']}

请只回复答案："""
        return self._call_llm(prompt).strip()

    def _solve_match(self, q: dict) -> dict:
        """匹配题 → 返回 {selectName: value} 映射"""
        pairs_desc = []
        for p in q.get("pairs", []):
            opts = ", ".join(f"{o['value']}: {o['label']}" for o in p["options"])
            pairs_desc.append(f"  - \"{p['text']}\" 可选: [{opts}]")

        prompt = f"""你是一个答题助手。请完成以下匹配题，为每一项选择正确的匹配项。

题目：
{q['text']}

匹配项：
{chr(10).join(pairs_desc)}

请以 JSON 格式回复每个匹配项的 value 值，格式如：{{"item1": "matched_value", "item2": "matched_value2"}}
只回复 JSON，不要包含其他内容。"""
        raw = self._call_llm(prompt).strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            warn(f"匹配题 JSON 解析失败: {raw}")
            return {}

    def _solve_generic(self, q: dict) -> str:
        """未知题型的通用求解"""
        prompt = f"""你是一个答题助手。请回答以下题目，只回复答案，不要包含解释。

题目：
{q.get('text', '')}

请只回复答案："""
        return self._call_llm(prompt).strip()

    # ================================================================
    # LLM 调用
    # ================================================================

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM API，带重试"""
        if not self.client:
            raise RuntimeError("未配置 LLM API Key，请在 config.py 中设置 LLM_API_KEY")

        for attempt in range(self.config.MAX_RETRIES):
            try:
                resp = self.client.chat.completions.create(
                    model=self.config.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个精确的答题助手，只输出答案，不输出解释。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # 低温度确保答案稳定
                )
                return resp.choices[0].message.content or ""

            except Exception as e:
                error(f"LLM 调用失败 (第 {attempt + 1}/{self.config.MAX_RETRIES} 次): {e}")
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise

        return ""

    # ================================================================
    # 工具方法
    # ================================================================

    @staticmethod
    def _format_options(options: list[dict]) -> str:
        lines = []
        for opt in options:
            lines.append(f"  value={opt['value']}: {opt['label']}")
        return "\n".join(lines)
