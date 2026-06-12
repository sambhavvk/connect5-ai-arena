"""
Pure Monte Carlo Tree Search agent for Connect‑Five (9×10).
No neural network – uses random rollouts and UCB1.
"""

import numpy as np
import math

ROWS = 9
COLS = 10
WIN = 5


class MCTSNode:
    """Node in the MCTS tree."""
    def __init__(self, parent, action, board):
        self.parent = parent
        self.action = action          # column that led to this node (None for root)
        self.board = board            # board from perspective of player to move from this node
        self.children = {}            # action -> MCTSNode
        self.visits = 0
        self.value_sum = 0.0          # total reward from perspective of player who moved to reach this node (parent player)
        self.untried_actions = get_legal_columns(board)

    def is_terminal(self):
        return is_terminal(self.board)

    def fully_expanded(self):
        return len(self.untried_actions) == 0


class PureMCTSAgent:
    def __init__(self, iterations=1000, exploration_constant=1.4):
        self.iterations = iterations
        self.c = exploration_constant

    def choose_action(self, board: np.ndarray, valid_actions: list) -> int:
        """
        board : (2, ROWS, COLS) from current player's perspective.
        valid_actions : e.g. [0,2,5,...]
        Returns chosen column (0-9).
        """
        root = MCTSNode(None, None, board.copy())

        for _ in range(self.iterations):
            node = self._select(root)
            reward = self._simulate(node.board)
            self._backpropagate(node, reward)

        # Choose child with highest visit count
        best_action = max(root.children, key=lambda a: root.children[a].visits)
        return best_action

    # ------------------------------------------------------------------
    # MCTS core steps
    # ------------------------------------------------------------------
    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select a leaf node to expand or simulate from."""
        while not node.is_terminal() and node.fully_expanded():
            # select child with best UCB1 score
            best_child = None
            best_ucb = -float("inf")
            for child in node.children.values():
                ucb = self._ucb_score(node, child)
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_child = child
            node = best_child

        # Expand if possible
        if not node.is_terminal() and not node.fully_expanded():
            return self._expand(node)
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Pick one untried action and create the corresponding child node."""
        action = node.untried_actions.pop()
        # Play the move from node's perspective, get opponent's view
        child_board, _ = make_move(node.board, action)
        child_node = MCTSNode(node, action, child_board)
        node.children[action] = child_node
        return child_node

    def _simulate(self, board: np.ndarray) -> float:
        """
        Run random rollout until terminal.
        Returns reward from perspective of player who is to move in the given board.
        """
        state = board.copy()
        # If already terminal (e.g. opponent won), return immediately
        if is_terminal(state):
            return terminal_reward(state)   # -1, 0, or +1

        while True:
            legal = get_legal_columns(state)
            action = np.random.choice(legal)
            state, win = make_move_and_check_win(state, action)
            if win:
                # The player who just moved (i.e., the one whose turn it was) won
                return 1.0
            # Check draw (no legal moves)
            if len(get_legal_columns(state)) == 0:
                return 0.0

    def _backpropagate(self, node: MCTSNode, reward: float):
        """
        Propagate outcome upward.
        At each step we flip the sign because a reward for a node's player
        means the opposite for its parent.
        """
        current_reward = reward
        while node is not None:
            node.visits += 1
            node.value_sum += current_reward
            current_reward = -current_reward
            node = node.parent

    def _ucb_score(self, parent: MCTSNode, child: MCTSNode) -> float:
        """UCB1 formula for child from perspective of parent's player."""
        if child.visits == 0:
            return float("inf")   # encourage exploration of unvisited nodes
        exploitation = child.value_sum / child.visits
        exploration = self.c * math.sqrt(math.log(parent.visits) / child.visits)
        return exploitation + exploration


# ----------------------------------------------------------------------
# Stateless game logic functions (used by both Minimax and MCTS)
# ----------------------------------------------------------------------
def make_move(board: np.ndarray, col: int):
    """
    Apply move by current player (channel 0).
    Returns new_board (opponent's view) and row where piece landed.
    """
    occupied = board[0] + board[1]
    row = np.where(occupied[:, col] == 0)[0][0]   # first empty from bottom
    new_board = board.copy()
    new_board[0, row, col] = 1.0
    # Swap perspective
    opp_view = np.stack([new_board[1], new_board[0]], axis=0)
    return opp_view, row


def make_move_and_check_win(board: np.ndarray, col: int):
    """
    Like make_move but also returns a boolean indicating whether
    this move created a win (for the player who moved, i.e. channel 0 before swap).
    """
    occupied = board[0] + board[1]
    row = np.where(occupied[:, col] == 0)[0][0]
    new_board = board.copy()
    new_board[0, row, col] = 1.0
    # Check if this move produced 5 in a row for player channel 0
    won = check_win_at(new_board, row, col, player_idx=0)
    # Swap perspective for next player
    opp_view = np.stack([new_board[1], new_board[0]], axis=0)
    return opp_view, won


def check_win_at(board: np.ndarray, row: int, col: int, player_idx: int) -> bool:
    """Check if player_idx has WIN in a row intersecting (row, col)."""
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
    """Return columns with empty space at top."""
    top = board[0, -1, :] + board[1, -1, :]
    return [c for c in range(COLS) if top[c] < 2]


def is_terminal(board: np.ndarray) -> bool:
    """
    Return True if the game is over.
    In this board, the player to move cannot have already won.
    Terminal if opponent (channel 1) has a win, or board full.
    """
    # Check if opponent has 5 in a row
    if full_board_has_win(board, player_idx=1):
        return True
    # Draw: no legal moves
    return len(get_legal_columns(board)) == 0


def terminal_reward(board: np.ndarray) -> float:
    """
    Reward from perspective of player to move in the given board.
    Must only be called when is_terminal(board) is True.
    """
    if full_board_has_win(board, player_idx=1):
        return -1.0   # opponent won
    return 0.0        # draw


def full_board_has_win(board: np.ndarray, player_idx: int) -> bool:
    """Full scan for a win (used when we don't know last move)."""
    layer = board[player_idx]
    for r in range(ROWS):
        for c in range(COLS - WIN + 1):
            if np.all(layer[r, c:c+WIN] == 1):
                return True
    for c in range(COLS):
        for r in range(ROWS - WIN + 1):
            if np.all(layer[r:r+WIN, c] == 1):
                return True
    for r in range(ROWS - WIN + 1):
        for c in range(COLS - WIN + 1):
            if all(layer[r+i, c+i] == 1 for i in range(WIN)):
                return True
    for r in range(WIN-1, ROWS):
        for c in range(COLS - WIN + 1):
            if all(layer[r-i, c+i] == 1 for i in range(WIN)):
                return True
    return False