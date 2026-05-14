"""答题历史 API"""
from fastapi import APIRouter

router = APIRouter(tags=["history"])

@router.get("/history")
async def list_history():
    return []

@router.get("/history/{session_id}")
async def get_history_detail(session_id: str):
    return {}
