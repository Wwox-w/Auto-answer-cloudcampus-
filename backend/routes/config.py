"""配置管理 API"""
from fastapi import APIRouter

router = APIRouter(tags=["config"])

@router.get("/config")
async def get_config():
    return {}

@router.put("/config")
async def update_config(data: dict):
    return {"status": "saved"}
