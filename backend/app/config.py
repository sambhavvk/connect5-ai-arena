# backend/app/config.py
import sys
from functools import lru_cache

# ---------- Robust import of BaseSettings ----------
BaseSettings = None
error_msg = ""

# Try pydantic-settings (official package for Pydantic v2)
try:
    from pydantic_settings import BaseSettings
except ImportError as e1:
    error_msg += f"pydantic_settings not found ({e1}). "
    # Fallback to Pydantic v1 native BaseSettings
    try:
        from pydantic import BaseSettings
    except ImportError as e2:
        error_msg += f"Nor pydantic BaseSettings ({e2})."

if BaseSettings is None:
    raise RuntimeError(
        "Unable to import BaseSettings.\n"
        "If you use Pydantic v2, install pydantic-settings:\n"
        "    pip install pydantic-settings\n\n"
        f"Detailed errors: {error_msg}"
    )


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./connect5.db"
    POLICY_NET_ONNX_PATH: str = "ml/ml/models/policy_net.onnx"
    VALUE_NET_ONNX_PATH: str = "ml/ml/models/value_net.onnx"
    MCTS_ITERATIONS: int = 800
    MCTS_C_PUCT: float = 2.5
    DEFAULT_OPPONENT: str = "mcts_nn"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()