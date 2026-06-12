"""
Minimax agent with alpha-beta pruning for Connect‑Five (9×10 board, 5 in a row).
"""

import numpy as np

ROWS = 9
COLS = 10
WIN = 5


class MinimaxAgent:
    def __init__(self, max_depth: int = 4):
        self.max_depth = max_depth

    # ------------------ public API ------------------
    def choose_action(self, board: np.ndarray, valid_actions: list) -> int:
        """board: (2, ROWS, COLS) from current player's perspective.
           valid_actions: list of legal columns.
           Returns chosen column (0-9)."""
        best_score = -float("inf")
        best_col = valid_actions[0]

        for col in valid_actions:
            new_board, row = self._make_move(board, col)
            # check for immediate win
            if self._is_win_at(new_board, row, col, player_idx=1):
                # The move wins instantly – choose it
                return col  # we can prune, no better is possible
            score = self._alpha_beta(new_board, self.max_depth - 1,
                                     -float("inf"), float("inf"))
            if score > best_score:
                best_score = score
                best_col = col
        return best_col

    # -------------- game mechanics (private) --------------
    @staticmethod
    def _make_move(board: np.ndarray, col: int):
        """
        Apply move by current player (channel 0), and return:
          - new_board: board from opponent's perspective (channels swapped)
          - row: row index where the piece landed (0 = bottom)
        """
        occupied = board[0] + board[1]  # shape (ROWS, COLS)
        col_data = occupied[:, col]
        row = np.where(col_data == 0)[0][0]  # first empty from bottom

        new_board = board.copy()
        new_board[0, row, col] = 1.0

        # swap perspective for opponent
        opp_view = np.stack([new_board[1], new_board[0]], axis=0)
        return opp_view, row

    @staticmethod
    def _is_win_at(board: np.ndarray, row: int, col: int, player_idx: int) -> bool:
        """
        Check if player_idx (0 or 1) has WIN in a row passing through (row, col).
        board: (2, ROWS, COLS) – caller must know which channel belongs to which player.
        """
        piece_layer = board[player_idx]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # positive direction
            r, c = row + dr, col + dc
            while 0 <= r < ROWS and 0 <= c < COLS and piece_layer[r, c] == 1:
                count += 1
                r += dr
                c += dc
            # negative direction
            r, c = row - dr, col - dc
            while 0 <= r < ROWS and 0 <= c < COLS and piece_layer[r, c] == 1:
                count += 1
                r -= dr
                c -= dc
            if count >= WIN:
                return True
        return False

    @staticmethod
    def _get_legal_columns(board: np.ndarray) -> list:
        top = board[0, -1, :] + board[1, -1, :]  # top row (index -1)
        return [c for c in range(COLS) if top[c] < 2]

    def _alpha_beta(self, board: np.ndarray, depth: int,
                    alpha: float, beta: float) -> float:
        """
        board: always from perspective of player whose turn it is.
        Returns score for **that player** (maximizing).
        """
        # Check if the last move (by opponent) already won.
        # The opponent's pieces are in channel1 of the current board.
        if self._player_has_win(board, player_idx=1):
            # The player who just moved (opponent) won → current player lost
            return -1.0 + depth * 0.001  # prefer later loss (small incentive to delay)

        valid = self._get_legal_columns(board)
        if not valid:
            return 0.0

        if depth == 0:
            return self._evaluate(board)

        # Maximize with respect to current player's moves
        score = -float("inf")
        for col in valid:
            child_board, row = self._make_move(board, col)
            # If this move wins immediately for current player (pieces in channel1 of child)
            if self._is_win_at(child_board, row, col, player_idx=1):
                return 1.0 - depth * 0.001  # prefer earlier wins
            val = self._alpha_beta(child_board, depth - 1, -beta, -alpha)
            score = max(score, val)
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return score

    @staticmethod
    def _player_has_win(board: np.ndarray, player_idx: int) -> bool:
        """Full board scan for win – only called at terminal/depth 0 for safety."""
        layer = board[player_idx]
        # horizontal
        for r in range(ROWS):
            for c in range(COLS - WIN + 1):
                if np.all(layer[r, c:c+WIN] == 1):
                    return True
        # vertical
        for c in range(COLS):
            for r in range(ROWS - WIN + 1):
                if np.all(layer[r:r+WIN, c] == 1):
                    return True
        # diag (down-right)
        for r in range(ROWS - WIN + 1):
            for c in range(COLS - WIN + 1):
                if all(layer[r+i, c+i] == 1 for i in range(WIN)):
                    return True
        # diag (up-right)
        for r in range(WIN-1, ROWS):
            for c in range(COLS - WIN + 1):
                if all(layer[r-i, c+i] == 1 for i in range(WIN)):
                    return True
        return False

    # --------------- heuristic evaluation ---------------
    @staticmethod
    def _evaluate(board: np.ndarray) -> float:
        """
        Heuristic score for the current player.
        Positive means good for current player (channel 0), negative for opponent.
        """
        own = board[0]
        opp = board[1]
        score = 0.0
        # Weights: longer lines are exponentially more valuable
        weights = {2: 2, 3: 5, 4: 50, 5: 1000}
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - WIN + 1):
                window_own = own[r, c:c+WIN]
                window_opp = opp[r, c:c+WIN]
                score += _window_score(window_own, window_opp, weights)
        # Vertical
        for c in range(COLS):
            for r in range(ROWS - WIN + 1):
                window_own = own[r:r+WIN, c]
                window_opp = opp[r:r+WIN, c]
                score += _window_score(window_own, window_opp, weights)
        # Diag down-right
        for r in range(ROWS - WIN + 1):
            for c in range(COLS - WIN + 1):
                window_own = np.array([own[r+i, c+i] for i in range(WIN)])
                window_opp = np.array([opp[r+i, c+i] for i in range(WIN)])
                score += _window_score(window_own, window_opp, weights)
        # Diag up-right
        for r in range(WIN-1, ROWS):
            for c in range(COLS - WIN + 1):
                window_own = np.array([own[r-i, c+i] for i in range(WIN)])
                window_opp = np.array([opp[r-i, c+i] for i in range(WIN)])
                score += _window_score(window_own, window_opp, weights)
        return score


def _window_score(own_slice: np.ndarray, opp_slice: np.ndarray,
                  weights: dict) -> float:
    """
    Score a single 5-cell window.
    own_slice, opp_slice: binary arrays (1 = piece, 0 = empty) of length WIN.
    """
    own_count = int(own_slice.sum())
    opp_count = int(opp_slice.sum())
    if own_count > 0 and opp_count > 0:
        return 0.0  # blocked window
    if own_count == 0 and opp_count == 0:
        return 0.0
    if own_count > 0:
        return weights.get(own_count, 0)
    else:  # opp_count > 0
        return -weights.get(opp_count, 0)