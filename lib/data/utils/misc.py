from pathlib import Path

from lib.config import logger


def get_files(folder: Path) -> list[Path]:
    """
    Recursively collect all files within a folder.

    Parameters
    ----------
    folder : Path
        Root folder to scan.

    Returns
    -------
    list of Path
        A list containing paths to all files in the folder (recursively).

    Raises
    ------
    ValueError
        If the provided path points to a file rather than a folder.

    Notes
    -----
    Subdirectories are traversed depth-first.

    Examples
    --------
    >>> files = Deduplicator.get_files(Path("dataset"))
    >>> len(files)
    128
    """
    all_files = []

    if folder.is_file():
        logger.debug(f"Provided path is a file: {folder}")
        raise ValueError("The provided path is a file, expected a folder.")

    for file_path in folder.iterdir():
        if file_path.is_file():
            all_files.append(file_path)

        if file_path.is_dir():
            logger.debug(f"Found subfolder: {file_path}")
            all_files.extend(get_files(file_path))

    return all_files
