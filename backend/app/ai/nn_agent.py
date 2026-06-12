"""
NN-guided MCTS agent for Connect‑Five (9×10).
Uses a policy network (ONNX) to guide tree search with PUCT, and random rollouts for value.
"""
import numpy as np
import math
import onnxruntime as ort

ROWS = 9
COLS = 10
WIN = 5


class MCTSNodeNN:
    """MCTS node used with a prior probability from the policy network."""
    def __init__(self, parent, action, board, prior=0.0):
        self.parent = parent
        self.action = action          # column that led to this node (None for root)
        self.board = board            # board from perspective of player to move from this node
        self.children = {}            # action -> MCTSNodeNN
        self.visits = 0
        self.value_sum = 0.0          # sum of rewards from perspective of parent's player (the one who moved to reach this node)
        self.prior = prior            # P(s, a) from policy network (for parent's edge)
        self.untried_actions = get_legal_columns(board)

    def is_terminal(self):
        return is_terminal(self.board)

    def fully_expanded(self):
        return len(self.untried_actions) == 0


class NNAgent:
    def __init__(self, onnx_path, iterations=800, c_puct=1.0):
        self.iterations = iterations
        self.c_puct = c_puct
        # Load ONNX model
        self.session = ort.InferenceSession(onnx_path)
        self.input_name = self.session.get_inputs()[0].name

    def choose_action(self, board: np.ndarray, valid_actions: list) -> int:
        """
        board : (2, ROWS, COLS) from current player's perspective.
        valid_actions : list of columns that are legal.
        Returns chosen column (0-9).
        """
        root = MCTSNodeNN(None, None, board.copy())

        for _ in range(self.iterations):
            # 1. Selection
            node = self._select(root)
            # 2. Expansion (if not terminal)
            if not node.is_terminal():
                node = self._expand(node)
            # 3. Simulation
            reward = self._simulate(node.board)
            # 4. Backpropagation
            self._backpropagate(node, reward)

        # Choose child with most visits
        best_action = max(root.children, key=lambda a: root.children[a].visits)
        return best_action

    # ------------------------------------------------------------------
    # MCTS core
    # ------------------------------------------------------------------
    def _select(self, node: MCTSNodeNN) -> MCTSNodeNN:
        """Descend to a leaf node using PUCT."""
        while not node.is_terminal() and node.fully_expanded():
            best_uct = -float("inf")
            best_child = None
            # total visits of parent
            total_n = node.visits
            for child in node.children.values():
                # PUCT formula
                if child.visits == 0:
                    # Ensure unvisited children get a chance
                    uct = float("inf")  # or high value
                else:
                    q_value = child.value_sum / child.visits
                    u_value = self.c_puct * child.prior * math.sqrt(total_n) / (1 + child.visits)
                    uct = q_value + u_value
                if uct > best_uct:
                    best_uct = uct
                    best_child = child
            node = best_child
        return node

    def _expand(self, node: MCTSNodeNN) -> MCTSNodeNN:
        """Expand node using policy network to assign prior probabilities."""
        # Get policy priors from ONNX model
        priors = self._get_policy_priors(node.board, node.untried_actions)
        # For each untried action, create a child node with its prior
        # We'll expand only one (pick randomly or by prior? Typically we expand one node at a time in simple MCTS.
        # To be computationally efficient, we'll expand the one with the highest prior (or random).
        # We'll pick one action to expand (the one with highest prior) and create that child.
        if not node.untried_actions:
            return node
        # Choose action with highest prior among untried
        action = max(node.untried_actions, key=lambda a: priors.get(a, 0))
        node.untried_actions.remove(action)
        # Apply move to get child board (opponent's view)
        child_board, _ = make_move(node.board, action)
        child_node = MCTSNodeNN(node, action, child_board, prior=priors.get(action, 0.0))
        node.children[action] = child_node
        return child_node

    def _simulate(self, board: np.ndarray) -> float:
        """Random rollout until terminal. Returns reward from perspective of player to move in given board."""
        state = board.copy()
        if is_terminal(state):
            return terminal_reward(state)

        while True:
            legal = get_legal_columns(state)
            action = np.random.choice(legal)
            state, win = make_move_and_check_win(state, action)
            if win:
                # The player who just moved (i.e., the one whose turn it was) won
                return 1.0
            if len(get_legal_columns(state)) == 0:
                return 0.0

    def _backpropagate(self, node: MCTSNodeNN, reward: float):
        """Propagate reward up, flipping sign at each level."""
        while node is not None:
            node.visits += 1
            node.value_sum += reward
            reward = -reward
            node = node.parent

    def _get_policy_priors(self, board: np.ndarray, valid_actions: list) -> dict:
        """Run ONNX model to get action probabilities for a single board, mask illegal ones, and return dict {col: prob}."""
        # Prepare input: (1, 2, 9, 10)
        input_array = board[np.newaxis, ...].astype(np.float32)
        logits = self.session.run(None, {self.input_name: input_array})[0][0]  # shape (10,)
        # Mask illegal actions
        mask = np.ones(COLS, dtype=bool)
        for a in range(COLS):
            if a not in valid_actions:
                mask[a] = False
        # Set illegal logits to -inf so softmax gives 0
        masked_logits = np.where(mask, logits, -np.inf)
        # Softmax
        max_logit = np.max(masked_logits)
        exp_logits = np.exp(masked_logits - max_logit)
        probs = exp_logits / np.sum(exp_logits)
        # Build dict
        priors = {a: float(probs[a]) for a in valid_actions}
        return priors


# ----------------------------------------------------------------------
# Game logic helpers (same as in pure MCTS, placed here for self‑containment)
# ----------------------------------------------------------------------
def make_move(board: np.ndarray, col: int):
    """Apply move by current player (channel 0). Returns new_board (opponent's view) and row."""
    occupied = board[0] + board[1]
    row = np.where(occupied[:, col] == 0)[0][0]
    new_board = board.copy()
    new_board[0, row, col] = 1.0
    opp_view = np.stack([new_board[1], new_board[0]], axis=0)
    return opp_view, row


def make_move_and_check_win(board: np.ndarray, col: int):
    """Like make_move but also returns boolean win."""
    occupied = board[0] + board[1]
    row = np.where(occupied[:, col] == 0)[0][0]
    new_board = board.copy()
    new_board[0, row, col] = 1.0
    won = check_win_at(new_board, row, col, player_idx=0)
    opp_view = np.stack([new_board[1], new_board[0]], axis=0)
    return opp_view, won


def check_win_at(board: np.ndarray, row: int, col: int, player_idx: int) -> bool:
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
    top = board[0, -1, :] + board[1, -1, :]
    return [c for c in range(COLS) if top[c] < 2]


def is_terminal(board: np.ndarray) -> bool:
    if full_board_has_win(board, player_idx=1):
        return True
    return len(get_legal_columns(board)) == 0


def terminal_reward(board: np.ndarray) -> float:
    if full_board_has_win(board, player_idx=1):
        return -1.0
    return 0.0


def full_board_has_win(board: np.ndarray, player_idx: int) -> bool:
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