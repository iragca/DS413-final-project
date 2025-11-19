import questionary

from .base_menu import BaseMenu
from .deduplicate_files import DeduplicateFilesMenu
from .download_dataset import DownloadDatasetMenu
from .splitter_menu import SplitterMenu


class AppMenu(BaseMenu):
    def menu(self) -> None:
        while True:
            choice = questionary.select(
                f"{self.breadcrumbs} >",
                choices=[
                    "Download Datasets",
                    "Deduplicate Dataset",
                    "Split Dataset",
                ],
            ).ask()

            match choice:
                case "Download Datasets":
                    DownloadDatasetMenu(self.breadcrumb_path)()
                case "Deduplicate Dataset":
                    DeduplicateFilesMenu(self.breadcrumb_path)()
                case "Split Dataset":
                    SplitterMenu(self.breadcrumb_path)()
                case None:
                    break
                case _:
                    questionary.print(f"Unknown choice: {choice}")
                    break

    @property
    def name(self) -> str:
        return "Main Menu"
