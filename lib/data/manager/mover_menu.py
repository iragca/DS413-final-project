from pathlib import Path

import questionary

from lib.config import Directories, logger

from .base_menu import BaseMenu


class MoverMenu(BaseMenu):
    """
    This menu allows moving files between folders within a specified directory.
    Specifically for the unhealthy leaves, when downloading datasets from different sources,
    with inconsistent folder structures but similar categories.
    """

    def menu(self) -> None:
        source_folder = questionary.path(
            "Enter the source folder path:",
        ).ask()

        if source_folder is None:
            return

        if not Path(source_folder).exists():
            questionary.print("Source folder does not exist.")
            return

        source_folder = Path(source_folder)

        logger.debug(f"Source folder selected: {source_folder}")

        if questionary.confirm("Custom destination?", default=False).ask():
            unhealthy_folder = Path(questionary.path("Enter unhealthy folder:").ask())
            healthy_folder = Path(questionary.path("Enter healthy folder:").ask())
        else:
            unhealthy_folder = Directories.INTERIM_DATA_DIR.value / "leaves" / "unhealthy"
            healthy_folder = Directories.INTERIM_DATA_DIR.value / "leaves" / "healthy"

        if not unhealthy_folder.exists():
            questionary.print("Destination folder does not exist.")
            return

        subclass_folders = [folder for folder in unhealthy_folder.iterdir() if folder.is_dir()]

        while True:
            chosen_folder = questionary.select(
                "Choose a folder:",
                choices=[folder.name for folder in source_folder.iterdir() if folder.is_dir()],
            ).ask()

            if chosen_folder is None:
                break

            chosen_folder = source_folder / chosen_folder

            move_to_folder = questionary.select(
                "Choose a folder to move to:",
                choices=[folder.name for folder in subclass_folders] + [healthy_folder.name],
            ).ask()

            if move_to_folder is None:
                break

            if move_to_folder == healthy_folder.name:
                destination_folder = healthy_folder
            else:
                destination_folder = unhealthy_folder / move_to_folder

            files_to_moves = [file for file in chosen_folder.iterdir()]
            for file in files_to_moves:
                destination_path = destination_folder / file.name
                file.rename(destination_path)
                logger.debug(f"Moved file {file} to {destination_path}")

            chosen_folder.rmdir()

            if questionary.confirm("Do you want to move more files?", default=True).ask() is False:
                break

    @property
    def name(self) -> str:
        return "Folder Mover"

    def find_subfiles(self, dir: Path) -> list[Path]:
        """
        Recursively find all files in a directory and its subdirectories.

        Parameters
        ----------
        dir : Path
            The root directory to search for files.

        Returns
        -------
        list of Path
            A list of ``Path`` objects representing all files found within
            the directory and its subdirectories.
        """
        files = []

        if dir.is_dir():
            for item in dir.iterdir():
                if item.is_file():
                    files.append(item)
                elif item.is_dir():
                    files.extend(self.find_subfiles(item))
        else:
            raise ValueError(f"{dir} is not a valid directory.")

        return files
