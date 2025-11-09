from enum import Enum
import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
_PROJ_ROOT = Path(__file__).resolve().parents[1]


class Directories(Enum):
    PROJ_ROOT = _PROJ_ROOT
    DATA_DIR = PROJ_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    INTERIM_DATA_DIR = DATA_DIR / "interim"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    EXTERNAL_DATA_DIR = DATA_DIR / "external"

    MODELS_DIR = PROJ_ROOT / "models"

    REPORTS_DIR = PROJ_ROOT / "reports"
    FIGURES_DIR = REPORTS_DIR / "figures"
    LOGS_DIR = REPORTS_DIR / "logs"


class Environments(Enum):
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")


logger.remove(0)
logger.add(Directories.LOGS_DIR.value / "runtime.log", mode="w", level="DEBUG")

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.add(
        lambda msg: tqdm.write(msg, end=""), colorize=True, level=Environments.LOGGING_LEVEL.value
    )
except ModuleNotFoundError:
    import sys

    logger.add(sys.stderr, colorize=True, level=Environments.LOGGING_LEVEL.value)

logger.debug(f"Project root directory: {Directories.PROJ_ROOT.value}")
