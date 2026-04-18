"""
Pydantic 스키마 — API 요청/응답 검증
"""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field
from domain.models import EntityType, SpaceType, DeviceType, AgentType


# ──────────────────────────────────────────────
# Entity
# ──────────────────────────────────────────────

class EntityBase(BaseModel):
    name: str
    owner_id: str | None = None
    metadata_: dict[str, Any] | None = Field(None, alias="metadata")

    model_config = {"populate_by_name": True}


class EntityResponse(EntityBase):
    id: str
    entity_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# ──────────────────────────────────────────────
# Space
# ──────────────────────────────────────────────

class SpaceCreate(EntityBase):
    space_type: SpaceType = SpaceType.HOME
    parent_space_id: str | None = None
    geometry_ref: str | None = None
    location: dict[str, float] | None = None


class SpaceResponse(EntityResponse):
    space_type: str
    parent_space_id: str | None = None
    geometry_ref: str | None = None
    location: dict[str, float] | None = None


# ──────────────────────────────────────────────
# Device
# ──────────────────────────────────────────────

class DeviceCreate(EntityBase):
    device_type: DeviceType = DeviceType.OTHER
    current_space_id: str | None = None
    capabilities: list[str] | None = None
    schema_id: str | None = None


class DeviceResponse(EntityResponse):
    device_type: str
    current_space_id: str | None = None
    capabilities: list[str] | None = None
    schema_id: str | None = None


class DeviceLocationUpdate(BaseModel):
    space_id: str


# ──────────────────────────────────────────────
# Agent
# ──────────────────────────────────────────────

class AgentCreate(EntityBase):
    agent_type: AgentType = AgentType.PERSON
    email: str | None = None
    password: str | None = None


class AgentResponse(EntityResponse):
    agent_type: str
    email: str | None = None


# ──────────────────────────────────────────────
# 상태 (Redis)
# ──────────────────────────────────────────────

class StateUpdate(BaseModel):
    """보안 Level 1: 서버는 정규화된 값 배열만 저장"""
    eid: str                    # 난독화된 entity ID
    v: list[float]              # 정규화된 값 (0~1)
    ts: int | None = None       # Unix timestamp (없으면 서버가 설정)


class StateResponse(BaseModel):
    eid: str
    v: list[float]
    ts: int


# ──────────────────────────────────────────────
# 이벤트
# ──────────────────────────────────────────────

class EventLog(BaseModel):
    entity_id: str
    event_type: str
    payload: dict[str, Any] | None = None


class EventResponse(BaseModel):
    id: int
    entity_id: str
    event_type: str
    payload: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
