from pathlib import Path

import questionary

from lib.config import Directories, logger
from lib.data.utils import Deduplicator

from .base_menu import BaseMenu


class DeduplicateFilesMenu(BaseMenu):
    def menu(self) -> None:
        folder_path = questionary.path(
            "Enter the path to save the flood control dataset:",
            default=str(Directories.INTERIM_DATA_DIR.value / "leaves"),
        ).ask()

        if folder_path is None:
            return

        strategy = questionary.select(
            "Select deduplication strategy:",
            choices=[
                "keep_first",
                "keep_last",
                "keep_random",
            ],
        ).ask()

        if strategy is None:
            return

        deduplicator = Deduplicator()
        deduplicator.deduplicate_folder(Path(folder_path), strategy=strategy)
        logger.success("Deduplication complete.")

    @property
    def name(self) -> str:
        return "Deduplicate Files"
