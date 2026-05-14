"""
题目解析器 —— 从 Moodle 答题页面提取题目结构化数据
"""

from playwright.sync_api import Page
from utils.logger import info, warn


def parse_questions(page: Page) -> list[dict]:
    """从当前页面提取所有题目，返回结构化列表"""
    questions = page.evaluate('''() => {
        const results = [];

        // ============================================================
        // 辅助：提取题目文本（多级回退）
        // ============================================================
        function getQuestionText(q) {
            // 按优先级尝试
            const selectors = [
                '.qtext',
                '.formulation .clearfix',
                '.content .formulation',
                '.formulation',
                '.info + .content',
            ];
            for (const sel of selectors) {
                const el = q.querySelector(sel);
                if (el) {
                    // 排除子结构中的例子、测试结果等，只取题目描述
                    const clone = el.cloneNode(true);
                    clone.querySelectorAll(
                        '.coderunner-examples, .coderunner-test-results, ' +
                        '.answer, .im-feedback, .outcome, .specificfeedback, ' +
                        '.questionflag, .state, .grade'
                    ).forEach(e => e.remove());
                    const text = clone.innerText?.trim();
                    if (text && text.length > 3) return text;
                }
            }
            // 最终回退
            return q.innerText?.substring(0, 500)?.trim() || '';
        }

        // ============================================================
        // 辅助：提取选项文本
        // ============================================================
        function getOptionLabel(inp) {
            // 尝试多种方式找到选项文本
            const strategies = [
                () => inp.closest('label')?.innerText?.trim(),
                () => {
                    const wrapper = inp.closest('.r0, .r1, .d-flex, .flex-fill, .answer-item, .option');
                    return wrapper?.querySelector('label')?.innerText?.trim() ||
                           wrapper?.querySelector('.option-text, .answer-text')?.innerText?.trim();
                },
                () => {
                    // Moodle 4.x: label 可能在 input 后面
                    const parent = inp.parentElement;
                    const label = parent?.querySelector('label');
                    return label?.innerText?.trim();
                },
                () => {
                    // 纯文本兄弟节点
                    const parent = inp.parentElement;
                    return parent?.innerText?.replace(inp.value || '', '').trim();
                },
            ];
            for (const fn of strategies) {
                const result = fn();
                if (result && result.length > 0 && result !== inp.value) return result;
            }
            return inp.value;
        }

        // ============================================================
        // 1. CodeRunner 编程题
        // ============================================================
        document.querySelectorAll('.que.coderunner').forEach((q) => {
            const textarea = q.querySelector('textarea.coderunner-answer');
            const exampleDiv = q.querySelector('.coderunner-examples');

            // 提取模板代码：优先取 textarea 当前内容（最完整），其次 data-reload-text
            let template = '';
            if (textarea) {
                // textarea.value 是用户已输入或预填的完整代码
                const currentVal = textarea.value?.trim() || '';
                // data-reload-text 是原始模板
                const reloadText = textarea.getAttribute('data-reload-text') || '';
                // 取更长的那个（更完整）
                template = currentVal.length >= reloadText.length ? currentVal : reloadText;
            }

            // 也尝试从 ACE 编辑器获取（可能比 textarea 更新）
            let aceContent = '';
            if (textarea) {
                const aceId = textarea.id ? textarea.id.replace(/^id_/, 'ace_') : '';
                const aceEl = aceId ? document.getElementById(aceId) : null;
                if (aceEl && window.ace) {
                    try {
                        aceContent = ace.edit(aceEl).getValue()?.trim() || '';
                    } catch(e) {}
                }
            }
            // ACE 内容如果更长，用 ACE 的
            if (aceContent.length > template.length) {
                template = aceContent;
            }

            const langSelect = q.querySelector('.coderunner-lang-select, select[id*="language"]');
            const language = langSelect ? langSelect.value : 'python3';

            results.push({
                type: 'coderunner',
                id: q.id,
                text: getQuestionText(q),
                examples: exampleDiv ? exampleDiv.innerText.trim() : '',
                answerName: textarea ? textarea.name : '',
                template: template,
                language: language
            });
        });

        // ============================================================
        // 2. 选择题（multichoice — 单选/多选）
        // ============================================================
        document.querySelectorAll('.que.multichoice').forEach((q) => {
            // 先精确查找 .answer 内的选项
            let checkboxes = q.querySelectorAll('.answer input[type="checkbox"]');
            let radios = q.querySelectorAll('.answer input[type="radio"]');

            // 回退：Moodle 4.x 选项可能在 .answer 之外
            if (checkboxes.length === 0 && radios.length === 0) {
                checkboxes = q.querySelectorAll('input[type="checkbox"]');
                radios = q.querySelectorAll('input[type="radio"]');
            }

            const isMulti = checkboxes.length > 0;
            const inputs = isMulti ? checkboxes : radios;

            const options = [];
            inputs.forEach(inp => {
                options.push({
                    value: inp.value,
                    label: getOptionLabel(inp),
                    name: inp.name,
                    checked: inp.checked
                });
            });

            if (options.length > 0) {
                results.push({
                    type: isMulti ? 'multichoice_multi' : 'multichoice',
                    id: q.id,
                    text: getQuestionText(q),
                    options: options
                });
            }
        });

        // ============================================================
        // 3. 判断题 (truefalse)
        // ============================================================
        document.querySelectorAll('.que.truefalse').forEach((q) => {
            const options = [];
            q.querySelectorAll('.answer input[type="radio"]').forEach(inp => {
                options.push({
                    value: inp.value,
                    label: getOptionLabel(inp),
                    name: inp.name,
                    checked: inp.checked
                });
            });

            if (options.length > 0) {
                results.push({
                    type: 'truefalse',
                    id: q.id,
                    text: getQuestionText(q),
                    options: options
                });
            }
        });

        // ============================================================
        // 4. 填空题 (shortanswer / numerical)
        // ============================================================
        document.querySelectorAll('.que.shortanswer, .que.numerical').forEach((q) => {
            const input = q.querySelector(
                'input[type="text"]:not([style*="display:none"]), ' +
                'input[type="number"], ' +
                'input.form-control'
            );
            if (input) {
                results.push({
                    type: 'shortanswer',
                    id: q.id,
                    text: getQuestionText(q),
                    inputName: input.name,
                    inputType: q.classList.contains('numerical') ? 'number' : 'text',
                    prefill: input.value || ''
                });
            }
        });

        // ============================================================
        // 5. 匹配题 (match / ddmatch)
        // ============================================================
        document.querySelectorAll('.que.match, .que.ddmatch').forEach((q) => {
            const pairs = [];

            // 下拉匹配
            q.querySelectorAll('table.answer tr, .answer select').forEach(el => {
                if (el.tagName === 'SELECT') {
                    const opts = [];
                    el.querySelectorAll('option').forEach(opt => {
                        if (opt.value) opts.push({value: opt.value, label: opt.innerText.trim()});
                    });
                    if (opts.length > 0) {
                        // 找关联的文本标签
                        const row = el.closest('tr');
                        const labelCell = row?.querySelector('td:first-child, th');
                        pairs.push({
                            text: labelCell?.innerText?.trim() || '',
                            selectName: el.name,
                            options: opts
                        });
                    }
                } else if (el.querySelector('select')) {
                    // 已经是 tr 级别，跳过
                }
            });

            // 拖拽匹配（ddmatch）— 有隐藏的 select 或 input
            if (pairs.length === 0) {
                q.querySelectorAll('select, input[type="hidden"][name*="ddmatch"]').forEach(el => {
                    if (el.name) {
                        pairs.push({
                            text: '',
                            selectName: el.name,
                            options: []
                        });
                    }
                });
            }

            if (pairs.length > 0) {
                results.push({
                    type: 'match',
                    id: q.id,
                    text: getQuestionText(q),
                    pairs: pairs
                });
            }
        });

        // ============================================================
        // 6. 未识别题型 — 兜底
        // ============================================================
        const knownTypes = [
            'coderunner', 'multichoice', 'truefalse',
            'shortanswer', 'numerical', 'match', 'ddmatch'
        ];
        document.querySelectorAll('.que').forEach(q => {
            const isKnown = knownTypes.some(t => q.classList.contains(t));
            if (isKnown) return;
            if (q.classList.contains('informationitem')) return;
            if (q.classList.contains('description')) return;
            if (q.classList.contains('category')) return;
            if (q.querySelector('.state')?.innerText?.includes('Not yet answered') === false &&
                q.querySelector('.state')?.innerText?.includes('Completed') === false) {
                // 跳过非题目区块
                if (!q.querySelector('.qtext, .formulation, input, textarea, select')) return;
            }

            results.push({
                type: 'unknown',
                id: q.id,
                text: getQuestionText(q),
                raw: q.className
            });
        });

        return results;
    }''')

    # 重新编号
    for i, q in enumerate(questions):
        q['number'] = i + 1

    info(f"解析到 {len(questions)} 道题目: " +
         ", ".join(f"#{q['number']}({q['type']})" for q in questions))
    return questions
