# backend/app/services/board_utils.py
import numpy as np

ROWS = 9
COLS = 10
WIN = 5

def make_move(board: np.ndarray, col: int, player: int = 0):
    """
    Apply a move for the given player (0 or 1).
    Returns:
        new_board (np.array): opponent's perspective (channels swapped)
        row (int): where the piece landed
    """
    occupied = board[0] + board[1]
    if col < 0 or col >= COLS:
        raise ValueError("Invalid column")
    if occupied[-1, col] != 0:
        raise ValueError("Column is full")

    row = np.where(occupied[:, col] == 0)[0][0]   # first empty from bottom
    new_board = board.copy()
    new_board[player, row, col] = 1.0

    # Swap channels so that the **next player** becomes channel 0
    opp_view = np.stack([new_board[1], new_board[0]], axis=0)
    return opp_view, row

def check_win_at(board: np.ndarray, row: int, col: int, player_idx: int = 0) -> bool:
    """
    Check if player_idx has WIN in a row intersecting (row, col).
    Works on a board where player_idx is the current channel 0.
    """
    piece_layer = board[player_idx]
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        count = 1
        r, c = row + dr, col + dc
        while 0 <= r < ROWS and 0 <= c < COLS and piece_layer[r, c] == 1:
            count += 1
            r += dr
            c += dc
        r, c = row - dr, col - dc
        while 0 <= r < ROWS and 0 <= c < COLS and piece_layer[r, c] == 1:
            count += 1
            r -= dr
            c -= dc
        if count >= WIN:
            return True
    return False

def get_legal_columns(board: np.ndarray) -> list:
    """Return list of non‑full columns."""
    top = board[0, -1, :] + board[1, -1, :]
    return [c for c in range(COLS) if top[c] == 0]

def is_draw(board: np.ndarray) -> bool:
    """True if no legal moves and no winner."""
    return len(get_legal_columns(board)) == 0

def board_to_2d_list(board: np.ndarray) -> list:
    """
    Convert a 2‑channel board to a 2D list where:
    0 = empty, 1 = player0, 2 = player1.
    """
    grid = np.zeros((ROWS, COLS), dtype=int)
    grid[board[0] == 1] = 1
    grid[board[1] == 1] = 2
    return grid.tolist()