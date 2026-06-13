from fastapi import APIRouter, HTTPException
from backend.app.services.replay_service import load_replay

router = APIRouter(tags=["replay"])

@router.get("/replay/{episode_id}")
async def get_replay(episode_id: str):
    """Return full step‑by‑step data for an uploaded episode."""
    replay = load_replay(episode_id)
    if not replay:
        raise HTTPException(status_code=404, detail="Episode not found")
    return replay