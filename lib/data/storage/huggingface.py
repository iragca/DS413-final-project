import os
from pathlib import Path
import tempfile
from typing import Union

from huggingface_hub import HfApi
from polars import DataFrame

from lib.config import Directories

from .storage import Storage


class HuggingFace(Storage):
    def __init__(self, token: Union[str, None] = os.getenv("HF_TOKEN")) -> None:
        super().__init__()
        if not token:
            raise ValueError("Hugging Face token must be provided.")

        self.api = HfApi(token=token)

    def save(self, data: Union[DataFrame, Path, str], repo_id: str) -> bool:
        """
        Save data to a Hugging Face repository.

        This method accepts either a Polars DataFrame or a file path (as a pathlib.Path or string)
        and delegates the actual saving work to an appropriate helper:
        - _save_dataframe for DataFrame objects
        - _save_file for file path inputs

        Parameters
        ----------
        data : polars.DataFrame | pathlib.Path | str
            The data to save. If a Polars DataFrame is provided, it will be serialized
            and uploaded via the DataFrame-saving routine. If a Path or string is
            provided, it is treated as a filesystem path to a file that will be uploaded.
        repo_id : str
            The identifier of the Hugging Face repository (for example "username/repo")
            where the data should be stored.

        Returns
        -------
        bool
            True if the save/upload operation completed successfully, False otherwise.
            The exact semantics of success/failure are determined by the underlying
            helper methods.

        Raises
        ------
        ValueError
            If `data` is not a Polars DataFrame, pathlib.Path, or string.
        Exception
            Any exceptions raised by the underlying helpers (_save_dataframe, _save_file)
            or the Hugging Face client/library may propagate through; callers should
            handle network and I/O related errors as appropriate.

        Notes
        -----
        - This method is a thin dispatcher and does not perform content-specific
          validation beyond type checking.
        - Ensure authentication and network connectivity are configured for uploads
          to the specified Hugging Face repository.

        Example
        -------
        >>> # Save a DataFrame
        >>> df = pl.DataFrame({"a": [1, 2, 3]})
        >>> client.save(df, "myuser/myrepo")
        >>> # Save a local file
        >>> client.save("/path/to/file.csv", "myuser/myrepo")
        """
        if isinstance(data, (Path, str)):
            return self._save_file(data, repo_id)

        if isinstance(data, DataFrame):
            return self._save_dataframe(data, repo_id)

        raise ValueError("Data must be either a Polars DataFrame or a file path.")

    def _save_dataframe(self, df: DataFrame, repo_id: str) -> bool:
        """
        Save a Polars DataFrame to a HuggingFace dataset repository.

        Parameters
        ----------
        df : DataFrame
            The Polars DataFrame to save.
        repo_id : str
            Identifier of the remote repository (dataset) to which the DataFrame will be uploaded.

        Returns
        -------
        bool
            True if the upload was initiated/completed successfully.

        Notes
        -----
        The DataFrame is first saved to a temporary CSV file, which is then uploaded
        to the specified HuggingFace dataset repository using `self.api.upload_file`.
        The temporary file is deleted after the upload.
        """
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as tmp_file:
            df.write_csv(tmp_file.name)
            self._save_file(Path(tmp_file.name), repo_id)

        return True

    def _save_file(self, file: Union[Path, str], repo_id: str) -> bool:
        """
        Save a file to a HuggingFace dataset repository.

        Parameters
        ----------
        file : Union[pathlib.Path, str]
            Path to the file to be uploaded.

        repo_id : str
            Identifier of the remote repository (dataset) to which the file will be uploaded.

        Returns
        -------
        bool
            True if the upload was initiated/completed successfully.

        Raises
        ------
            Exception: Propagates any exception raised by resolve_path, validate_file, or
                self.api.upload_file (for example file-not-found, validation failures, or API/network errors).
        """
        file = self.resolve_path(file)
        self.validate_file(file)
        self.api.upload_file(
            path_or_fileobj=file,
            path_in_repo="/",
            repo_id=repo_id,
            repo_type="dataset",
        )

        return True

    def load(
        self,
        repo_id: str,
        filename: str,
        save_dir: Union[Path, str] = Directories.EXTERNAL_DATA_DIR.value / "huggingface",
    ) -> Path:
        """
        Download a file from a Hugging Face dataset repository and save it into a local directory.

        This method uses the instance's `api.hf_hub_download` to fetch `filename` from the dataset
        repository identified by `repo_id` (repo_type="dataset"). The downloaded file is copied
        into `save_dir` (created if necessary) using `copy_file_to_directory` with mode "hardlink",
        and then renamed to `filename` inside `save_dir`. The returned Path points to the saved file.

        Args:
            repo_id (str): The identifier of the Hugging Face dataset repository (e.g. "owner/dataset").
            filename (str): The name of the file to download from the dataset repo.
            save_dir (Union[Path, str], optional): Destination directory to store the downloaded file.
                Defaults to Directories.EXTERNAL_DATA_DIR.value / "huggingface". Can be a Path or a string.

        Returns:
            Path: Absolute Path to the saved file in `save_dir` (i.e. save_dir / filename).

        Raises:
            Exception: If the downloaded file does not exist after `hf_hub_download`.
            Any exception raised by `self.api.hf_hub_download`, `self.resolve_path`, `Path.mkdir`,
            `copy_file_to_directory`, `Path.rename`, or underlying OS calls may propagate (e.g. OSError,
            PermissionError). Note that behavior of `Path.rename` regarding overwriting an existing
            target file can be platform-dependent.

        Side effects:
            - Creates `save_dir` if it does not exist.
            - Attempts to create a hard link to the downloaded file in `save_dir` (via
              `copy_file_to_directory` with mode "hardlink"). If hardlinking is not possible,
              the implementation of `copy_file_to_directory` may fall back to copying.
            - Renames the stored file to `filename` inside `save_dir`.

        Example:
            >>> storage.load("owner/dataset", "data.csv")
            PosixPath("/abs/path/to/external_data/huggingface/data.csv")
        """
        downloaded_file = Path(
            self.api.hf_hub_download(
                repo_id=repo_id,
                repo_type="dataset",
                filename=filename,
            )
        ).resolve()

        if not downloaded_file.exists():
            raise Exception(f"Failed to download file {filename} from repo {repo_id}.")

        save_dir = self.resolve_path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        saved_file = self.copy_file_to_directory(
            source_file=downloaded_file,
            target_directory=save_dir,
            mode="hardlink",
        )
        new_name = save_dir / filename
        saved_file.rename(new_name)
        return new_name
