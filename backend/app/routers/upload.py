from fastapi import APIRouter, HTTPException, UploadFile, File
import json
from backend.app.services.replay_service import store_episode

router = APIRouter(tags=["upload"])

@router.post("/upload")
async def upload_episode(file: UploadFile = File(...)):
    """Accept an OpenSpiel episode JSON file and store it in the DB."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files allowed")

    content = await file.read()
    try:
        episode = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Validate basic episode structure
    if "states" not in episode or "actions" not in episode:
        raise HTTPException(status_code=400, detail="Missing required episode fields")

    episode_id = store_episode(episode)
    return {"message": "Episode uploaded", "episode_id": episode_id}