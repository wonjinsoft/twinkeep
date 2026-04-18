"""
TwinKeep 도메인 모델
Entity → Space / Device / Agent 계층 구조
"""
from datetime import datetime
from enum import Enum
from typing import Any
from sqlalchemy import String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ──────────────────────────────────────────────
# Enum 정의
# ──────────────────────────────────────────────

class EntityType(str, Enum):
    SPACE = "space"
    DEVICE = "device"
    AGENT = "agent"


class SpaceType(str, Enum):
    HOME = "home"
    ROOM = "room"
    OFFICE = "office"
    BUILDING = "building"
    FACTORY = "factory"
    OTHER = "other"


class DeviceType(str, Enum):
    PHONE = "phone"
    SENSOR = "sensor"
    EQUIPMENT = "equipment"
    APPLIANCE = "appliance"
    PET = "pet"
    PERSON = "person"
    OTHER = "other"


class AgentType(str, Enum):
    PERSON = "person"
    SERVICE = "service"
    EXTERNAL_SYSTEM = "external_system"


# ──────────────────────────────────────────────
# Entity (기본 테이블)
# ──────────────────────────────────────────────

class Entity(Base):
    """모든 트윈 객체의 기본 단위"""
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    entity_type: Mapped[str] = mapped_column(String(20))           # space / device / agent
    name: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[str | None] = mapped_column(String(36), nullable=True)  # Agent ID
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    access_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 접근 규칙
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Space(Base):
    """공간 — 계층적으로 중첩 가능 (집 > 거실 > 책상 위)"""
    __tablename__ = "spaces"

    id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id"), primary_key=True)
    space_type: Mapped[str] = mapped_column(String(50))
    parent_space_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("spaces.id"), nullable=True)
    geometry_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)  # USD 파일 경로
    location: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {lat, lng, alt}
    boundary_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 공개 범위


class Device(Base):
    """기기 — 공간 안에 존재, 이동 가능"""
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id"), primary_key=True)
    device_type: Mapped[str] = mapped_column(String(50))
    current_space_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("spaces.id"), nullable=True)
    capabilities: Mapped[list | None] = mapped_column(JSON, nullable=True)  # ["temperature", "humidity"]
    schema_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 로컬 스키마 참조 (보안 Level 1)


class Agent(Base):
    """행위자 — 공간/기기를 소유하고 접근을 제어"""
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id"), primary_key=True)
    agent_type: Mapped[str] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)


# ──────────────────────────────────────────────
# 이벤트 이력 (PostgreSQL)
# ──────────────────────────────────────────────

class EntityEvent(Base):
    """상태 변경 이력"""
    __tablename__ = "entity_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entity_id: Mapped[str] = mapped_column(String(36))  # FK 없음 — 자유 형식
    event_type: Mapped[str] = mapped_column(String(100))  # state_change / control / register
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
