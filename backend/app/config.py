# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # ------- Database -------
    DATABASE_URL: str = "sqlite:///./connect5.db"

    # ------- AI Model Paths (used by NN agent) -------
    POLICY_NET_ONNX_PATH: str = "ml/models/policy_net.onnx"
    VALUE_NET_ONNX_PATH: str  = "ml/models/value_net.onnx"

    # ------- MCTS Hyperparameters -------
    MCTS_ITERATIONS: int = 800
    MCTS_C_PUCT: float = 2.5

    # ------- Agent Selection Defaults -------
    DEFAULT_OPPONENT: str = "mcts_nn"   # "minimax", "mcts_pure", "mcts_nn"

    class Config:
        env_file = ".env"           # local overrides
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()