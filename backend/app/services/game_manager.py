# backend/app/services/game_manager.py
import numpy as np
from backend.app.services import board_utils as bu

class GameManager:
    """
    Manages the state of a single Connect5 game.
    Assumes Player 0 = Human (or caller), Player 1 = AI (the agent).
    """

    def __init__(self, ai_agent):
        """
        ai_agent: an object with a method choose_action(board, valid_actions) -> int.
        """
        self.ai_agent = ai_agent
        # Board: 2 planes (player0, player1) shape (2,9,10).
        # Initially empty, current player = 0
        self.board = np.zeros((2, bu.ROWS, bu.COLS), dtype=np.float32)
        self.current_player = 0   # 0 = human, 1 = AI
        self.winner = None        # 0, 1, or None (draw/ongoing)

    def valid_columns(self) -> list:
        """Return list of columns that are not full."""
        return bu.get_legal_columns(self.board)

    def get_board_2d(self) -> list:
        """Return a 2D grid for the frontend."""
        return bu.board_to_2d_list(self.board)

    def player_move(self, col: int):
        """
        Process a human move.
        Returns: (win: bool, new board 2D list)
        Raises ValueError if column invalid or game already over.
        """
        if self.winner is not None:
            raise ValueError("Game already finished")
        if self.current_player != 0:
            raise ValueError("Not human's turn")
        if col not in self.valid_columns():
            raise ValueError("Illegal move (column full)")

        # Apply move
        self.board, row = bu.make_move(self.board, col, player=0)
        # Did player 0 win?
        if bu.check_win_at(self.board, row, col, player_idx=1):
            self.winner = 0
            return True, self.get_board_2d()

        self.current_player = 1
        return False, self.get_board_2d()

    def ai_move(self):
        """
        Let the AI choose and execute a move.
        Returns: (column, win: bool, new board 2D list)
        Assumes it's currently AI's turn.
        """
        if self.winner is not None:
            raise ValueError("Game already finished")
        if self.current_player != 1:
            raise ValueError("Not AI's turn")

        valid = self.valid_columns()
        col = self.ai_agent.choose_action(self.board, valid)

        self.board, row = bu.make_move(self.board, col, player=1)
        # After make_move swaps channels, AI's piece is now on channel 0
        if bu.check_win_at(self.board, row, col, player_idx=0):
            self.winner = 1
            return col, True, self.get_board_2d()

        self.current_player = 0
        return col, False, self.get_board_2d()

    def is_draw(self):
        """True if board full and no winner."""
        return bu.is_draw(self.board) and self.winner is None