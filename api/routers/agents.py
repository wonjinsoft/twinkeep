"""Agent API — /agents"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.models import Entity, Agent, Space, Device, EntityType
from domain.schemas import AgentCreate, AgentResponse
from services.database import get_db

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(data: AgentCreate, db: AsyncSession = Depends(get_db)):
    eid = str(uuid.uuid4())
    entity = Entity(id=eid, entity_type=EntityType.AGENT, name=data.name,
                    owner_id=data.owner_id, metadata_=data.metadata_)
    agent = Agent(id=eid, agent_type=data.agent_type.value, email=data.email)
    db.add(entity)
    await db.flush()  # entities INSERT 먼저 확정 후 agents INSERT
    db.add(agent)
    await db.commit()
    return {**entity.__dict__, **agent.__dict__}


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Entity, agent_id)
    agent = await db.get(Agent, agent_id)
    if not entity or not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {**entity.__dict__, **agent.__dict__}


@router.get("/{agent_id}/spaces")
async def get_owned_spaces(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Entity).where(
        Entity.owner_id == agent_id,
        Entity.entity_type == EntityType.SPACE
    ))
    entities = result.scalars().all()
    spaces = []
    for e in entities:
        s = await db.get(Space, e.id)
        if s:
            spaces.append({**e.__dict__, **s.__dict__})
    return spaces


@router.get("/{agent_id}/devices")
async def get_owned_devices(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Entity).where(
        Entity.owner_id == agent_id,
        Entity.entity_type == EntityType.DEVICE
    ))
    entities = result.scalars().all()
    devices = []
    for e in entities:
        d = await db.get(Device, e.id)
        if d:
            devices.append({**e.__dict__, **d.__dict__})
    return devices
