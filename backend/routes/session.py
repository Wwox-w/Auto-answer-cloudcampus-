"""答题会话 API"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.storage import read_config
from backend.ws.progress import progress_manager
from backend.engine.answer_engine import AnswerEngine

router = APIRouter(tags=["session"])

_engine: AnswerEngine | None = None


@router.post("/session/start")
async def start_session():
    global _engine
    config = read_config()
    _engine = AnswerEngine(config, progress_manager.create_callback())
    progress_manager.set_engine(_engine)
    _engine.start()
    return {"status": "started"}


@router.post("/session/stop")
async def stop_session():
    global _engine
    if _engine and _engine.running:
        _engine.stop()
    return {"status": "stopped"}
