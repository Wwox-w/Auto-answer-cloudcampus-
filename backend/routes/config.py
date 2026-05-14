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
