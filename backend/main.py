"""Auto-Answer Web 后端入口

启动方式（从项目根目录）:
    uvicorn backend.main:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.config import router as config_router
from backend.routes.session import router as session_router
from backend.routes.history import router as history_router
from backend.ws.progress import progress_manager

app = FastAPI(title="Auto-Answer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config_router, prefix="/api")
app.include_router(session_router, prefix="/api")
app.include_router(history_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws/progress")
async def ws_progress_endpoint(ws: WebSocket):
    await progress_manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "heartbeat":
                await ws.send_json({"type": "heartbeat", "status": "alive"})
            elif data.get("type") == "confirm_code":
                await ws.send_json({"type": "code_confirmed"})
    except Exception:
        progress_manager.disconnect(ws)
