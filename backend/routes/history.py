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
