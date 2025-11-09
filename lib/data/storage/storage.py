from abc import ABC, abstractmethod
from pathlib import Path
import shutil
from typing import Any, Literal, Union


class Storage(ABC):
    @abstractmethod
    def save(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def load(self, *args, **kwargs) -> Any:
        pass

    @staticmethod
    def resolve_path(path: Union[Path, str]) -> Path:
        """
        Convert a path-like input into a pathlib.Path instance.

        Parameters
        ----------
        path : Union[pathlib.Path, str]
            A filesystem path given either as a pathlib.Path or as a string.

        Returns
        -------
        pathlib.Path
            A pathlib.Path instance representing the given path. If a Path
            instance is provided it is returned unchanged.

        Notes
        -----
        This is a lightweight convenience helper: it does not expand user
        home (~), resolve symbolic links, or check whether the path exists.
        Use pathlib.Path.expanduser(), Path.resolve(), or Path.exists() as
        needed after conversion.

        Examples
        --------
        >>> resolve_path("some/file.txt")
        PosixPath('some/file.txt')
        >>> resolve_path(Path("some/file.txt"))
        PosixPath('some/file.txt')
        """
        if isinstance(path, str):
            return Path(path)
        return path

    def copy_file_to_directory(
        self,
        source_file: Union[Path, str],
        target_directory: Union[Path, str],
        mode: Literal["copy", "move", "hardlink"] = "copy",
        override: bool = True,
    ) -> Path:
        """
        Copy, move, or create a hard link for a file into a target directory.

        Parameters
        ----------
        source_file : Union[pathlib.Path, str]
            Path to the source file to operate on. Will be resolved via self.resolve_path
            before validation.
        target_directory : Union[pathlib.Path, str]
            Path to the destination directory. Will be resolved via self.resolve_path
            and validated with self.validate_directory.
        mode : Literal["copy", "move", "hardlink"], optional
            Operation to perform:
              - "copy": copy the file metadata and contents to the target directory
                using shutil.copy2.
              - "move": move the file into the target directory using shutil.move
                (source will no longer exist at the original location on success).
              - "hardlink": create a hard link inside the target directory pointing to
                the original file (target filename will be source_file.name). Hard links
                require the same filesystem and appropriate permissions.
            Default is "copy".
        override : bool, optional
            Whether to override the target file if it already exists. If False and
            the target file exists, a FileExistsError will be raised. Default is True.

        Returns
        -------
        Path
            The path to the copied/moved/hardlinked file.

        Raises
        ------
        ValueError
            If `mode` is not one of "copy", "move", or "hardlink".
        FileNotFoundError, PermissionError, OSError
            Propagates exceptions raised by path resolution, validation, or the underlying
            file operations (shutil.copy2, shutil.move, os.link). For example, creating
            a hard link on a different filesystem will raise an OSError.
        FileExistsError
            If the target file already exists and `override` is False.

        Examples
        --------
        # copy:
        self.copy_file_to_directory("/tmp/data.csv", "/var/data", mode="copy")

        # move:
        self.copy_file_to_directory(Path("a.txt"), Path("/archive"), mode="move")

        # hard link:
        self.copy_file_to_directory("report.pdf", "/shared/reports", mode="hardlink")
        """
        source_file = self.resolve_path(source_file)
        target_directory = self.resolve_path(target_directory)
        target_directory.mkdir(parents=True, exist_ok=True)

        self.validate_file(source_file)
        self.validate_directory(target_directory)

        target_file = target_directory / source_file.name

        if target_file.exists():
            if override:
                target_file.unlink()
            else:
                raise FileExistsError(f"Target file already exists: {target_file}")

        match mode:
            case "copy":
                shutil.copy(source_file, target_file)
            case "move":
                shutil.move(source_file, target_file)
            case "hardlink":
                target_file.hardlink_to(source_file)
            case _:
                raise ValueError(f"Unsupported file operation mode: {mode}")

        return target_file

    @staticmethod
    def validate_directory(directory: Path) -> Path:
        """
        Validate that the provided Path points to an existing directory.

        Parameters
        ----------
        directory : pathlib.Path
            The path to validate.

        Returns
        -------
        pathlib.Path
            The same Path object if it exists and is a directory.

        Raises
        ------
        ValueError
            If the path does not exist:
                "Provided directory does not exist: {directory}"
            If the path exists but is not a directory:
                "Provided path is not a directory: {directory}"

        Examples
        --------
        >>> from pathlib import Path
        >>> p = Path('/tmp')
        >>> validate_directory(p)  # returns p if /tmp exists and is a directory
        """
        if not directory.exists():
            raise ValueError(f"Provided directory does not exist: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Provided path is not a directory: {directory}")

        return directory

    @staticmethod
    def validate_file(file_path: Path) -> Path:
        """Validate that the provided Path exists and refers to a regular file.

        Parameters
        ----------
        file_path : pathlib.Path
            The filesystem path to validate.

        Returns
        -------
        pathlib.Path
            The same Path object when it exists and is a file.

        Raises
        ------
        ValueError
            If the path does not exist or if it exists but is not a file.
        """
        if not file_path.exists():
            raise ValueError(f"Provided file does not exist: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Provided path is not a file: {file_path}")

        return file_path
