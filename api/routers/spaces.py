"""Space API — /spaces"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.models import Entity, Space, Device, EntityType
from domain.schemas import SpaceCreate, SpaceResponse, DeviceResponse
from services.database import get_db

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.post("", response_model=SpaceResponse, status_code=201)
async def create_space(data: SpaceCreate, db: AsyncSession = Depends(get_db)):
    eid = str(uuid.uuid4())
    entity = Entity(id=eid, entity_type=EntityType.SPACE, name=data.name,
                    owner_id=data.owner_id, metadata_=data.metadata_)
    space = Space(id=eid, space_type=data.space_type.value,
                  parent_space_id=data.parent_space_id,
                  geometry_ref=data.geometry_ref, location=data.location)
    db.add(entity)
    await db.flush()
    db.add(space)
    await db.commit()
    return {**entity.__dict__, **space.__dict__}


@router.get("/{space_id}", response_model=SpaceResponse)
async def get_space(space_id: str, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Entity, space_id)
    space = await db.get(Space, space_id)
    if not entity or not space:
        raise HTTPException(status_code=404, detail="Space not found")
    return {**entity.__dict__, **space.__dict__}


@router.get("/{space_id}/children", response_model=list[SpaceResponse])
async def get_children(space_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Space).where(Space.parent_space_id == space_id))
    children = result.scalars().all()
    rows = []
    for s in children:
        e = await db.get(Entity, s.id)
        if e:
            rows.append({**e.__dict__, **s.__dict__})
    return rows


@router.get("/{space_id}/devices", response_model=list[DeviceResponse])
async def get_devices(space_id: str, db: AsyncSession = Depends(get_db)):
    from domain.models import Device
    result = await db.execute(select(Device).where(Device.current_space_id == space_id))
    devices = result.scalars().all()
    rows = []
    for d in devices:
        e = await db.get(Entity, d.id)
        if e:
            rows.append({**e.__dict__, **d.__dict__})
    return rows
