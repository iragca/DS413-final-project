import questionary
from questionary import Choice

from .base_menu import BaseMenu
from .deduplicate_files import DeduplicateFilesMenu
from .download_dataset import DownloadDatasetMenu
from .mover_menu import MoverMenu
from .splitter_menu import SplitterMenu


class AppMenu(BaseMenu):
    def menu(self) -> None:
        while True:
            choice = questionary.select(
                f"{self.breadcrumbs} >",
                choices=[
                    Choice(
                        "Download Datasets",
                        description="Download datasets from HuggingFace and Kaggle",
                    ),
                    Choice(
                        "Deduplicate Dataset",
                        description="Remove duplicate files from a specified directory",
                    ),
                    Choice(
                        "Split Dataset",
                        description="Split dataset into training, validation, and test sets",
                    ),
                    Choice(
                        "Move Files",
                        description="Move images/files between directories, was used for integrating datasets into MegaPlant",
                    ),
                ],
            ).ask()

            match choice:
                case "Download Datasets":
                    DownloadDatasetMenu(self.breadcrumb_path)()
                case "Deduplicate Dataset":
                    DeduplicateFilesMenu(self.breadcrumb_path)()
                case "Split Dataset":
                    SplitterMenu(self.breadcrumb_path)()
                case "Move Files":
                    MoverMenu(self.breadcrumb_path)()
                case None:
                    break
                case _:
                    questionary.print(f"Unknown choice: {choice}")
                    break

    @property
    def name(self) -> str:
        return "Main Menu"
