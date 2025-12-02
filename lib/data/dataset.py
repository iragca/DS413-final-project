from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path, PosixPath
from typing import Optional, Union

from beartype import beartype
from PIL import Image
from torch import Tensor
from torch.nn import Module
from torch.utils.data import Dataset
from torchvision.transforms import Compose


class ImageDataset(Dataset, ABC):
    @beartype
    def __init__(
        self,
        data_path: Union[str, Path, PosixPath],
        transforms: Optional[Union[Compose, Module]] = None,
    ):
        if isinstance(data_path, str):
            data_path = Path(data_path)

        self.data_path = data_path
        self.transforms = transforms

    @abstractmethod
    def data(self) -> list[tuple[Path, int]]:
        """
        List of all dataset samples.

        This property is computed once and cached on first access. It should be
        implemented by subclasses to return a list of ``(image_path, label)``
        pairs.

        Returns
        -------
        list of tuple
            A list of ``(image_path, label)`` pairs, where ``image_path`` is a
            ``Path`` object and ``label`` is an integer.
        """
        pass

    def __len__(self):
        """
        Return the number of samples in the dataset.

        Returns
        -------
        int
            Total number of images across all classes.
        """
        return len(self.data)

    def __getitem__(
        self, idx
    ) -> Union[tuple[Tensor, int], tuple[Image.Image, int], tuple[Union[Path, PosixPath], int]]:
        """
        Retrieve a single dataset sample.

        Loads an RGB image from disk and applies the optional transformation.
        If no transformations are provided, the method returns the image path
        instead of the loaded image. This allows lazy loading or custom
        processing pipelines.

        Parameters
        ----------
        idx : int
            Index of the sample to retrieve.

        Returns
        -------
        tuple[Union[Image.Image, Tensor, Path, PosixPath], int]
            If ``transforms`` is provided:
                ``(image, label)`` where ``image`` is a PIL ``Image`` or the
                output of the transform, and ``label`` is an integer.

            If ``transforms`` is None:
                ``(image_path, label)`` where ``image_path`` is a ``Path`` object.
        """
        image_path, label = self.data[idx]
        image = Image.open(image_path).convert("RGB")
        if self.transforms:
            return self.transforms(image), label
        else:
            return image_path, label

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

    @property
    def SYMPTOM_MAP(self) -> dict[str, int]:
        """
        Mapping of integer labels to symptom names for unhealthy plants.

        Returns
        -------
        dict of int to str
            Dictionary mapping integer labels to symptom names.
        """
        return {
            "blight": 0,
            "yellowing": 1,
            "malformation": 2,
            "powdery_mildew": 3,
            "feeding": 4,
            "mold": 5,
            "mosaic": 6,
            "rot": 7,
            "rust": 8,
            "scab": 9,
            "spot": 10,
            "scorch": 11,
        }


class MegaPlantDataset(ImageDataset):
    """
    Dataset class for loading healthy and unhealthy plant images.

    This dataset expects the following directory structure:

        data_path/
            healthy/
                image_1.jpg
                image_2.jpg
                ...
            unhealthy/
                image_3.jpg
                image_4.jpg
                ...

    The dataset assigns integer labels based on ``STATUS_MAP`` and optionally
    applies a set of transformations to each image.

    Parameters
    ----------
    data_path : Path
        Path to the root directory containing the ``healthy`` and ``unhealthy``
        subdirectories.
    transforms : callable, optional
        A callable transform (e.g., torchvision transforms) applied to each
        image. If ``None``, the dataset returns the image path instead of the
        loaded image.

    Attributes
    ----------
    data_path : str or Path or PosixPath
        Root folder containing image class subdirectories.
    transforms : Compose or Module, optional
        ``torchvision.transforms`` Transformations applied to each loaded image.
    data : list of tuple
        Cached list of ``(image_path, label)`` pairs generated on first access.
    STATUS_MAP : dict of str to int
        Mapping from class folder names to numerical labels.
    """

    @beartype
    def __init__(
        self,
        data_path: Union[str, Path, PosixPath],
        transforms: Optional[Union[Compose, Module]] = None,
    ):
        if isinstance(data_path, str):
            data_path = Path(data_path)

        self.data_path = data_path
        self.transforms = transforms

    @cached_property
    def data(self):
        """
        List of all dataset samples.

        This property is computed once and cached on first access. It iterates
        over all class subdirectories defined in ``STATUS_MAP`` and collects
        image paths paired with their corresponding integer labels.

        Returns
        -------
        list of tuple
            A list of ``(image_path, label)`` pairs, where ``image_path`` is a
            ``Path`` object and ``label`` is an integer.
        """
        healthy_files = self.find_subfiles(self.data_path / "healthy")
        unhealthy_files = self.find_subfiles(self.data_path / "unhealthy")

        data = []

        for image_path in healthy_files:
            data.append((image_path, self.STATUS_MAP["healthy"]))

        for image_path in unhealthy_files:
            data.append((image_path, self.STATUS_MAP["unhealthy"]))

        return data

    @property
    def STATUS_MAP(self) -> dict[str, int]:
        """
        Mapping of class names to integer labels.

        Returns
        -------
        dict of str to int
            Dictionary assigning ``0`` to ``"healthy"`` and ``1`` to
            ``"unhealthy"``.
        """
        return {
            "healthy": 0,
            "unhealthy": 1,
        }


class UnhealthyMegaPlantDataset(MegaPlantDataset):
    """
    Dataset class for loading unhealthy plant images with specific symptom labels.

    This dataset expects the following directory structure:
    unhealthy/
        blight/
        yellowing/
        malformation/
        mildew/
        mite/
        mold/
        mosaic/
        rot/
        rust/
        scab/
        spot/
        scorch/
    """

    @cached_property
    def data(self) -> list[tuple[Path, int]]:
        """
        List of all dataset samples for unhealthy plants.
        """
        data = []
        for symptom in self.SYMPTOM_MAP.keys():
            class_path = self.data_path / "unhealthy" / symptom
            for image_path in class_path.iterdir():
                if image_path.is_file():
                    data.append((image_path, self.SYMPTOM_MAP[symptom]))
        return data


class CombinedMegaPlantDataset(UnhealthyMegaPlantDataset):
    """
    Combined dataset class for loading both unhealthy symptoms and healthy plant images.
    """

    @cached_property
    def data(self) -> list[tuple[Path, int]]:
        """
        List of all dataset samples for both healthy and unhealthy plants.
        """
        data = super().data  # Get unhealthy data from parent class
        healthy_files = self.find_subfiles(self.data_path / "healthy")
        data.extend((image_path, self.CLASS_MAP["healthy"]) for image_path in healthy_files)
        return data

    @property
    def CLASS_MAP(self) -> dict[str, int]:
        """
        Mapping of class names to integer labels for both healthy and unhealthy plants.

        Returns
        -------
        dict of str to int
            Dictionary assigning integer labels to symptom names and "healthy".
        """
        max_class = max(self.SYMPTOM_MAP.values()) + 1

        return {
            **self.SYMPTOM_MAP,
            "healthy": max_class,
        }


class PlantDocDiseaseDetection(ImageDataset):
    """
    Dataset class for loading plant images from the PlantDoc dataset.
    """

    @cached_property
    def data(self) -> list[tuple[Path, int]]:
        """
        List of all dataset samples.

        This property is computed once and cached on first access. It iterates
        over all class subdirectories and collects image paths paired with their
        corresponding integer labels.

        Returns
        -------
        list of tuple
            A list of ``(image_path, label)`` pairs, where ``image_path`` is a
            ``Path`` object and ``label`` is an integer.
        """

        all_files = self.find_subfiles(self.data_path)

        data = []
        for file_path in all_files:
            if file_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue

            label = self.resolve_class(file_path)
            data.append((file_path, label))
        return data

    def resolve_class(self, filename: Path) -> int:
        """
        Determine the class label based on the filename.
        """
        for symptom in self.SYMPTOM_MAP.keys():
            if symptom in filename.parent.name.lower():
                return 1
        return 0


class PlantVillageDiseaseDetection(ImageDataset):
    """
    Dataset class for loading plant images from the PlantVillage dataset.
    """

    @cached_property
    def data(self) -> list[tuple[Path, int]]:
        """
        List of all dataset samples.

        This property is computed once and cached on first access. It iterates
        over all class subdirectories and collects image paths paired with their
        corresponding integer labels.

        Returns
        -------
        list of tuple
            A list of ``(image_path, label)`` pairs, where ``image_path`` is a
            ``Path`` object and ``label`` is an integer.
        """

        all_files = self.find_subfiles(self.data_path / "color")

        data = []
        for file_path in all_files:
            if file_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue

            label = self.resolve_class(file_path)
            data.append((file_path, label))
        return data

    def resolve_class(self, filename: Path) -> int:
        """
        Determine the class label based on the filename.
        """
        for symptom in self.SYMPTOM_MAP.keys():
            if symptom in filename.parent.name.lower():
                return 1
        return 0
