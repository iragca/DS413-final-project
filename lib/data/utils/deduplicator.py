from collections import defaultdict
import hashlib
from pathlib import Path
import random
from typing import Literal

from tqdm import tqdm

from lib.config import logger

type Strategy = Literal["keep_first", "keep_last", "keep_random"]


class Deduplicator:
    """
    Utility class for deduplicating files within a folder based on their contents.

    This class identifies duplicate files by computing MD5 hashes and deletes
    duplicates according to a chosen strategy. Deduplication is recursive and
    processes all files within subdirectories.

    Methods
    -------
    deduplicate_folder(folder, strategy)
        Deduplicate all files in a folder recursively.
    delete_files(files, strategy)
        Delete files according to a selected strategy for retaining one file.
    get_files(folder)
        Recursively list all files in the given folder.
    hash_file(file_path)
        Compute the MD5 hash of a file.
    """

    def deduplicate_folder(self, folder: Path, strategy: Strategy = "keep_first") -> None:
        """
        Deduplicate files inside a folder by deleting duplicates based on their hash.

        Parameters
        ----------
        folder : Path
            Path to the folder to deduplicate. Must be a directory.
        strategy : {"keep_first", "keep_last", "keep_random"}, optional
            Deduplication strategy determining which file to preserve:

            - `"keep_first"` (default): Keep the first encountered file.
            - `"keep_last"`: Keep the most recently encountered file.
            - `"keep_random"`: Keep a randomly selected file.

        Raises
        ------
        ValueError
            If the provided path points to a file rather than a folder.

        Notes
        -----
        The method computes an MD5 hash for each file. Files with identical hashes
        are considered duplicates.

        Examples
        --------
        >>> d = Deduplicator()
        >>> d.deduplicate_folder(Path("data"), strategy="keep_last")
        """
        logger.debug(f"Starting deduplication in folder: {folder} with strategy: {strategy}")

        if folder.is_file():
            logger.error("Provided path is a file, expected a folder.")
            raise ValueError("The provided path is a file, expected a folder.")

        seen_hashes = defaultdict(list)
        all_files = self.get_files(folder)
        logger.info(f"Found {len(all_files)} files in folder {folder}")

        for file_path in tqdm(all_files, desc="Hashing files"):
            file_hash = self.hash_file(file_path)
            seen_hashes[file_hash].append(file_path)

        # Identify duplicates
        for hash, files in tqdm(seen_hashes.items(), desc="Identifying duplicates"):
            if len(files) > 1:
                logger.debug(f"Found duplicates for hash {hash}: {[str(f) for f in files]}")
                self.delete_files(files, strategy)

    @staticmethod
    def delete_files(files: list[Path], strategy: Strategy = "keep_first") -> None:
        """
        Delete duplicate files based on a deduplication strategy.

        Parameters
        ----------
        files : list of Path
            List of file paths that share the same content hash.
        strategy : {"keep_first", "keep_last", "keep_random"}, optional
            Strategy used to determine which file to keep:

            - `"keep_first"` (default): Delete all except the first file.
            - `"keep_last"`: Delete all except the last file.
            - `"keep_random"`: Keep one random file and delete the rest.

        Raises
        ------
        ValueError
            If an unknown strategy string is provided.

        Notes
        -----
        This function performs file deletion using `Path.unlink()`.
        """
        match strategy:
            case "keep_first":
                files_to_delete = files[1:]
            case "keep_last":
                files_to_delete = files[:-1]
            case "keep_random":
                to_keep = random.choice(files)
                files_to_delete = [f for f in files if f != to_keep]
            case _:
                logger.error(f"Unknown strategy: {strategy}")
                raise ValueError(f"Unknown strategy: {strategy}")

        for file_path in files_to_delete:
            file_path.unlink()

    @staticmethod
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
                all_files.extend(Deduplicator.get_files(file_path))

        return all_files

    @staticmethod
    def hash_file(file_path: Path) -> str:
        """
        Compute the MD5 hash of a file.

        Parameters
        ----------
        file_path : Path
            Path to the file whose hash will be computed.

        Returns
        -------
        str
            The hexadecimal MD5 hash of the file.

        Notes
        -----
        Files are read in 4096-byte chunks to support hashing large files.

        Examples
        --------
        >>> Deduplicator.hash_file(Path("sample.txt"))
        'd41d8cd98f00b204e9800998ecf8427e'
        """

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        final_hash = hash_md5.hexdigest()
        logger.debug(f"Computed hash for {file_path}: {final_hash}")
        return final_hash
