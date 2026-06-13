# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.agents import agents        # <-- import from new module
from backend.app.routers import game, upload, replay, leaderboard

app = FastAPI(title="Connect5 AI Arena API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(game.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(replay.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "Connect5 AI Arena backend running"}

@app.get("/api/agents")
async def list_agents():
    return {name: agent is not None for name, agent in agents.items()}