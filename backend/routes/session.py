"""答题会话 API"""
from fastapi import APIRouter

router = APIRouter(tags=["session"])

@router.post("/session/start")
async def start_session():
    return {"status": "started"}

@router.post("/session/stop")
async def stop_session():
    return {"status": "stopped"}
