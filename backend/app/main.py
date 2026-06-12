# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import get_settings
from backend.app.ai.minimax_agent import MinimaxAgent
from backend.app.ai.mcts_agent import PureMCTSAgent
from backend.app.ai.nn_agent import NNAgent
from backend.app.routers import game, upload, replay, leaderboard

# ---------- Load Settings ----------
settings = get_settings()

# ---------- Initialize AI Agents (loaded once) ----------
agents = {}
# Minimax
agents["minimax"] = MinimaxAgent(max_depth=4)
# Pure MCTS
agents["mcts_pure"] = PureMCTSAgent(iterations=800)
# NN-guided MCTS – loads ONNX model
try:
    agents["mcts_nn"] = NNAgent(
        onnx_path=settings.POLICY_NET_ONNX_PATH,
        iterations=settings.MCTS_ITERATIONS,
        c_puct=settings.MCTS_C_PUCT,
    )
except Exception as e:
    print(f"Warning: Could not load NN agent: {e}")
    agents["mcts_nn"] = None   # will fallback gracefully

# ---------- FastAPI App ----------
app = FastAPI(title="Connect5 AI Arena API", version="1.0.0")

# Allow CORS (for local frontend dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Dependency: inject agents ----------
def get_agent(agent_type: str = "minimax"):
    """Return the requested agent instance."""
    agent = agents.get(agent_type)
    if agent is None:
        raise ValueError(f"Agent '{agent_type}' not available")
    return agent

# ---------- Mount Routers ----------
app.include_router(game.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(replay.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")

# ---------- Health check ----------
@app.get("/")
async def root():
    return {"status": "Connect5 AI Arena backend running"}

@app.get("/api/agents")
async def list_agents():
    """Return map of agent IDs and whether they are loaded."""
    return {name: agent is not None for name, agent in agents.items()}