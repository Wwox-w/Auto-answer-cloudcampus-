"""本地 JSON 文件存储"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
AUTH_FILE = BASE_DIR / "auth.json"
HISTORY_DIR = BASE_DIR / "history"
HISTORY_DIR.mkdir(exist_ok=True)


def _safe_history_path(session_id: str) -> Path:
    """构造安全的 history 文件路径，防止路径遍历"""
    f = (HISTORY_DIR / f"{session_id}.json").resolve()
    if not str(f).startswith(str(HISTORY_DIR.resolve())):
        raise ValueError(f"Invalid session_id: {session_id}")
    return f


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
            logger.warning(f"跳过损坏的历史文件: {f.name}")
    return results


def get_history_detail(session_id: str) -> dict | None:
    """获取某次答题的详细记录"""
    f = _safe_history_path(session_id)
    if f.exists():
        return json.loads(f.read_text())
    return None


def save_history(session_id: str, data: dict) -> None:
    """保存答题记录"""
    f = _safe_history_path(session_id)
    f.write_text(json.dumps(data, indent=2, ensure_ascii=False))
