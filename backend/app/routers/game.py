from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import uuid

from backend.app.services.game_manager import GameManager
from backend.app.agents import agents

router = APIRouter(tags=["game"])

# In‑memory store for active games (replace with DB in production)
active_games = {}

class StartGameResponse(BaseModel):
    game_id: str
    board: List[List[int]]          # 2D list for frontend
    current_player: int             # 0 or 1 (0 = human, 1 = AI)
    valid_columns: List[int]

class MoveRequest(BaseModel):
    column: int

class MoveResponse(BaseModel):
    game_id: str
    board: List[List[int]]
    current_player: int
    valid_columns: List[int]
    winner: Optional[int] = None   # 0, 1, or None (draw)
    ai_move_column: Optional[int] = None

@router.post("/game/start", response_model=StartGameResponse)
async def start_game(agent_type: str = "minimax"):
    """
    Create a new game. Player 0 = human (always to move first),
    Player 1 = AI of given agent_type.
    """
    if agent_type not in agents:
        raise HTTPException(status_code=400, detail=f"Unknown agent '{agent_type}'")

    manager = GameManager(ai_agent=agents[agent_type])
    game_id = str(uuid.uuid4())
    active_games[game_id] = manager

    return {
        "game_id": game_id,
        "board": manager.get_board_2d(),
        "current_player": 0,
        "valid_columns": manager.valid_columns()
    }

@router.post("/game/move", response_model=MoveResponse)
async def make_move(game_id: str, move: MoveRequest):
    """
    Submit a human move (column) and get AI response.
    """
    manager = active_games.get(game_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Game not found")

    if manager.current_player != 0:
        raise HTTPException(status_code=400, detail="Not your turn")

    try:
        win, board = manager.player_move(move.column)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check if human won
    if win:
        active_games.pop(game_id, None)
        return MoveResponse(
            game_id=game_id,
            board=board.tolist(),  # 2D
            current_player=0,
            valid_columns=[],
            winner=0
        )

    # AI's turn
    if manager.current_player == 1:
        ai_col, ai_win, board = manager.ai_move()
        if ai_win:
            active_games.pop(game_id, None)
            return MoveResponse(
                game_id=game_id,
                board=board.tolist(),
                current_player=1,
                valid_columns=[],
                winner=1,
                ai_move_column=ai_col
            )
        return MoveResponse(
            game_id=game_id,
            board=board.tolist(),
            current_player=0,
            valid_columns=manager.valid_columns(),
            ai_move_column=ai_col
        )

    # Draw check
    if manager.is_draw():
        active_games.pop(game_id, None)
        return MoveResponse(
            game_id=game_id,
            board=board.tolist(),
            current_player=0,
            valid_columns=[],
            winner=None
        )

    return MoveResponse(
        game_id=game_id,
        board=board.tolist(),
        current_player=0,
        valid_columns=manager.valid_columns()
    )