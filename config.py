import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'instance' / 'ldm.db').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CPB_PATH = os.getenv(
        "CPB_PATH",
        str(BASE_DIR.parent / "Conceptual-Personality-Builder"),
    )
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_FLASH = os.getenv("GEMINI_MODEL_FLASH", "gemini-2.0-flash")
    GEMINI_MODEL_EVAL = os.getenv("GEMINI_MODEL_EVAL", "gemini-2.0-flash")
    LLM_MOCK = os.getenv("LLM_MOCK", "0") == "1"

    # Stabilization weights
    STAB_W_TRUST = float(os.getenv("STAB_W_TRUST", "0.04"))
    STAB_W_RESPECT = float(os.getenv("STAB_W_RESPECT", "0.03"))
    STAB_W_RELATIONSHIP = float(os.getenv("STAB_W_RELATIONSHIP", "0.03"))
    STAB_W_STRESS = float(os.getenv("STAB_W_STRESS", "0.05"))
    STAB_W_FATIGUE = float(os.getenv("STAB_W_FATIGUE", "0.04"))
    STAB_COHESION_BONUS = float(os.getenv("STAB_COHESION_BONUS", "0.02"))

    COHESION_W_TRUST = 0.4
    COHESION_W_RESPECT = 0.35
    COHESION_W_RELATIONSHIP = 0.25

    EMOTIONAL_MOMENTUM = 0.15
    MEMORY_TRUST_DELTA_THRESHOLD = 3.0
    MAX_TURNS_PER_SCENARIO = 15
    MAX_MEMORIES_IN_PROMPT = 8
