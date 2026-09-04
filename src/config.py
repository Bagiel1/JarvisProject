from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# /home/bagiel/Gabriel/obsidian/ia_obsidian
OBSIDIAN_PATH = (
    Path.home()
    / "Gabriel"
    / "obsidian"
    / "ia_obsidian"
)

CHROMA_PATH = PROJECT_ROOT / "data" / "bunker_db"

JARVIS_MODEL = "claude-haiku-4-5-20251001"
CODER_MODEL = "claude-sonnet-4-5-20250929"

JARVIS_MAX_TOKENS = 1000
CODER_MAX_TOKENS = 4000

MODEL_PRICES = {
    JARVIS_MODEL: {
        "input": 1.0,
        "output": 5.0,
    },

    CODER_MODEL: {
        "input": 3.0,
        "output": 15.0,
    },
}