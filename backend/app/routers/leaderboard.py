from fastapi import APIRouter
from typing import List, Dict

router = APIRouter(tags=["leaderboard"])

# Stub: replace with real DB queries later
fake_ratings = [
    {"player": "NN-MCTS",   "elo": 1520},
    {"player": "Minimax",   "elo": 1485},
    {"player": "Pure MCTS", "elo": 1421},
    {"player": "Human 1",   "elo": 1350},
]

@router.get("/leaderboard")
async def get_leaderboard() -> List[Dict]:
    """Return the current Elo leaderboard."""
    return fake_ratings