"""WebSocket 进度管理器"""
import asyncio
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ProgressManager:
    """管理 WebSocket 连接，广播答题进度"""

    def __init__(self):
        self._connections: list[WebSocket] = []
        self._engine = None  # AnswerEngine 实例

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._connections.append(ws)
        logger.info(f"WebSocket 客户端已连接 (当前 {len(self._connections)} 个)")

    def disconnect(self, ws: WebSocket):
        if ws in self._connections:
            self._connections.remove(ws)
            logger.info(f"WebSocket 客户端已断开 (剩余 {len(self._connections)} 个)")

    def set_engine(self, engine):
        self._engine = engine

    async def broadcast(self, event: dict):
        """向所有连接的 WebSocket 推送事件"""
        dead = []
        for ws in self._connections:
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.remove(ws)

    def create_callback(self):
        """创建同步回调函数，线程安全地向事件循环推送事件"""
        loop = asyncio.get_event_loop()

        def on_event(event: dict):
            try:
                asyncio.run_coroutine_threadsafe(self.broadcast(event), loop)
            except Exception:
                pass

        return on_event

    def stop_engine(self):
        if self._engine and self._engine.running:
            self._engine.stop()


progress_manager = ProgressManager()
