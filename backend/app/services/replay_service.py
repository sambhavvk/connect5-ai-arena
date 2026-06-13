# backend/app/services/replay_service.py

# In‑memory store for uploaded episodes (replace with DB)
episode_store = {}

def store_episode(episode: dict) -> str:
    """Save an episode dict and return a unique ID."""
    import uuid
    ep_id = str(uuid.uuid4())
    episode_store[ep_id] = episode
    # TODO: persist to DB
    return ep_id

def load_replay(episode_id: str) -> dict:
    """Retrieve a stored episode by ID."""
    return episode_store.get(episode_id)