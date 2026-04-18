"""TwinKeep API — 진입점"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from services.database import init_db
from routers import spaces, devices, agents, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="TwinKeep API",
    description="Personal digital twin platform — connect any space, device, or agent",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spaces.router)
app.include_router(devices.router)
app.include_router(agents.router)
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
