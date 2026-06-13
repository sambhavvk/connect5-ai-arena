# backend/app/agents.py
from backend.app.config import get_settings
from backend.app.ai.minimax_agent import MinimaxAgent
from backend.app.ai.mcts_agent import PureMCTSAgent
from backend.app.ai.nn_agent import NNAgent

settings = get_settings()

agents = {
    "minimax": MinimaxAgent(max_depth=4),
    "mcts_pure": PureMCTSAgent(iterations=800),
}

# NN agent – load only if ONNX model exists
try:
    agents["mcts_nn"] = NNAgent(
        onnx_path=settings.POLICY_NET_ONNX_PATH,
        iterations=settings.MCTS_ITERATIONS,
        c_puct=settings.MCTS_C_PUCT,
    )
except Exception as e:
    print(f"Warning: Could not load NN agent: {e}")
    agents["mcts_nn"] = None