from pathlib import Path

import questionary

from lib.config import Directories, logger

from ..utils import mega_plant_split
from .base_menu import BaseMenu


class SplitterMenu(BaseMenu):
    def menu(self) -> None:
        data_path = questionary.path(
            "Enter the path to the MegaPlant dataset:",
            default=str(Directories.INTERIM_DATA_DIR.value / "leaves"),
        ).ask()

        if data_path is None:
            return

        destination_path = questionary.path(
            "Enter the destination path for the split dataset:",
            default=str(Path(data_path).parent / "megaplant_split"),
        ).ask()

        if destination_path is None:
            return

        split_type = questionary.select(
            "Select split type:",
            choices=[
                "Train/Validation",
                "Train/Validation/Test",
            ],
        ).ask()

        match split_type:
            case "Train/Validation":
                split_ratio_str = questionary.text(
                    "Enter the train/validation split ratio (space-separated, e.g., '0.8 0.2'):",
                    default="0.8 0.2",
                ).ask()
            case "Train/Validation/Test":
                split_ratio_str = questionary.text(
                    "Enter the train/validation/test split ratio (space-separated, e.g., '0.7 0.2 0.1'):",
                    default="0.7 0.2 0.1",
                ).ask()
            case None:
                return
            case _:
                logger.error("Invalid split type selected.")
                return

        if split_ratio_str is None:
            return

        split_ratio = [float(ratio) for ratio in split_ratio_str.split()]
        mega_plant_split(
            data=Path(data_path),
            split_ratio=split_ratio,
            destination=Path(destination_path),
        )

        logger.success("Dataset splitting complete.")

    @property
    def name(self) -> str:
        return "Dataset Splitter"
