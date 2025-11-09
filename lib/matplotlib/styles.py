from enum import Enum
from pathlib import Path


class Styles(Enum):
    """Enum for Matplotlib styles used in the project."""

    CMR10 = Path(__file__).parent / "cmr10.mplstyle"
    ML = Path(__file__).parent / "ml.mplstyle"
