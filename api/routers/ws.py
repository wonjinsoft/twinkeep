"""WebSocket — 실시간 상태 스트림"""
import asyncio
import json
import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.config import settings

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/devices")
async def ws_devices(websocket: WebSocket):
    """모든 device 상태 변경을 실시간으로 수신"""
    await websocket.accept()
    r = aioredis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe("twin:device:update")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe("twin:device:update")
        await r.aclose()


@router.websocket("/ws/spaces/{space_id}")
async def ws_space(websocket: WebSocket, space_id: str):
    """특정 공간의 device 상태만 필터링해서 수신"""
    await websocket.accept()
    r = aioredis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe("twin:device:update")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                # space_id가 payload에 포함된 경우만 전달
                if data.get("space_id") == space_id:
                    await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe("twin:device:update")
        await r.aclose()
