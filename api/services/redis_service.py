"""Redis 상태 레이어 — twin:{type}:{id}:state"""
import json
import time
import redis.asyncio as aioredis
from core.config import settings

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def _state_key(entity_type: str, entity_id: str) -> str:
    return f"twin:{entity_type}:{entity_id}:state"


async def set_state(entity_type: str, entity_id: str, values: list[float]) -> dict:
    """상태 저장 — 정규화된 값 배열만 저장 (보안 Level 1)"""
    r = await get_redis()
    ts = int(time.time())
    payload = {"eid": entity_id, "v": values, "ts": ts}
    await r.set(_state_key(entity_type, entity_id), json.dumps(payload))
    await r.publish(f"twin:{entity_type}:update", json.dumps(payload))
    return payload


async def get_state(entity_type: str, entity_id: str) -> dict | None:
    """상태 조회"""
    r = await get_redis()
    raw = await r.get(_state_key(entity_type, entity_id))
    if raw is None:
        return None
    return json.loads(raw)


async def delete_state(entity_type: str, entity_id: str):
    """상태 삭제"""
    r = await get_redis()
    await r.delete(_state_key(entity_type, entity_id))
