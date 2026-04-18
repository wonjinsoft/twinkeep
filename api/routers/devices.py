"""Device API — /devices"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models import Entity, Device, EntityType
from domain.schemas import DeviceCreate, DeviceResponse, DeviceLocationUpdate, StateUpdate, StateResponse
from services.database import get_db
from services import redis_service

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", response_model=DeviceResponse, status_code=201)
async def create_device(data: DeviceCreate, db: AsyncSession = Depends(get_db)):
    eid = str(uuid.uuid4())
    entity = Entity(id=eid, entity_type=EntityType.DEVICE, name=data.name,
                    owner_id=data.owner_id, metadata_=data.metadata_)
    device = Device(id=eid, device_type=data.device_type.value,
                    current_space_id=data.current_space_id,
                    capabilities=data.capabilities, schema_id=data.schema_id)
    db.add(entity)
    await db.flush()
    db.add(device)
    await db.commit()
    return {**entity.__dict__, **device.__dict__}


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Entity, device_id)
    device = await db.get(Device, device_id)
    if not entity or not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return {**entity.__dict__, **device.__dict__}


@router.put("/{device_id}/location", response_model=DeviceResponse)
async def update_location(device_id: str, data: DeviceLocationUpdate,
                          db: AsyncSession = Depends(get_db)):
    """기기 위치(소속 공간) 변경"""
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.current_space_id = data.space_id
    await db.commit()
    entity = await db.get(Entity, device_id)
    return {**entity.__dict__, **device.__dict__}


@router.get("/{device_id}/state", response_model=StateResponse | None)
async def get_state(device_id: str):
    """Redis에서 현재 상태 조회"""
    state = await redis_service.get_state("device", device_id)
    return state


@router.put("/{device_id}/state", response_model=StateResponse)
async def update_state(device_id: str, data: StateUpdate):
    """기기 상태 갱신 — 정규화된 값 배열 (보안 Level 1)"""
    return await redis_service.set_state("device", device_id, data.v)
