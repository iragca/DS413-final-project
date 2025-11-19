from pathlib import Path
import random
from typing import Optional

from tqdm import tqdm

from lib.config import logger

from .misc import get_files


def mega_plant_split(
    data: Path,
    split_ratio: list[float],
    destination: Path,
    seed: Optional[int] = None,
) -> None:
    """
    Split the MegaPlant dataset into train/val/(test) subsets using hardlinks.

    This function takes a dataset with the structure:

        data/
            healthy/
            unhealthy/

    and produces a directory:

        destination/{2_split or 3_split}/
            train/healthy/
            train/unhealthy/
            val/...
            test/...  (optional)

    Files are NOT copied; instead, hardlinks are created to save disk space.

    Parameters
    ----------
    data : Path
        Path to the dataset root containing ``healthy/`` and ``unhealthy/`` folders.
    split_ratio : list of float
        List of two or three ratios that must sum to 1.0.
        - Length 2 → splits into train/val
        - Length 3 → splits into train/val/test
    destination : Path
        Output directory where the split folders will be created.
    seed : int, optional
        Random seed for reproducible shuffling of file ordering.

    Raises
    ------
    ValueError
        If the split ratios are invalid or do not sum to 1.

    Notes
    -----
    - Hardlinks require the source and destination to be on the same filesystem.
    - Uses ``tqdm`` to show progress during file linking.
    """
    _validate_split_ratio(split_ratio)

    split_count = len(split_ratio)
    logger.info(f"Number of splits: {split_count}")

    split_root = _create_split_root(destination)
    all_images = _load_images(data)

    if seed is not None:
        random.seed(seed)

    random.shuffle(all_images)
    logger.info(f"Total images found: {len(all_images)}")

    splits = _compute_splits(all_images, split_ratio)
    _write_splits(split_root, splits)


# ----------------------------- Helpers -------------------------------- #


def _validate_split_ratio(split_ratio: list[float]) -> None:
    """
    Validate the format and values of the split ratio list.

    Parameters
    ----------
    split_ratio : list of float
        The list of ratios provided by the user.

    Raises
    ------
    ValueError
        If the ratios do not sum to 1,
        if any ratio is non-positive,
        or if the list length is not 2 or 3.
    """

    if sum(split_ratio) != 1.0:
        raise ValueError(f"Split ratios must sum to 1.0, but sum to {sum(split_ratio)}")

    if any(r <= 0 for r in split_ratio):
        raise ValueError("Split ratios must be greater than 0.0")

    if len(split_ratio) not in {2, 3}:
        raise ValueError(f"Split ratio must have length 2 or 3, but got length {len(split_ratio)}")


def _create_split_root(destination: Path) -> Path:
    """
    Create the output split directory.

    Parameters
    ----------
    destination : Path
        The parent directory for the generated split.

    Returns
    -------
    Path
        The created directory path.
    """
    split_root = destination
    split_root.mkdir(parents=True, exist_ok=True)
    return split_root


def _load_images(data: Path) -> list[tuple[Path, str]]:
    """
    Load all images from the dataset, labeling them by class.

    Parameters
    ----------
    data : Path
        Root dataset directory containing ``healthy`` and ``unhealthy`` subfolders.

    Returns
    -------
    list of tuple
        Each tuple contains ``(image_path, class_name)``.
    """
    all_images = []

    for class_name in ["unhealthy", "healthy"]:
        class_path = data / class_name
        for image in get_files(class_path):
            all_images.append((image, class_name))

    return all_images


def _compute_splits(
    all_images: list[tuple[Path, str]], split_ratio: list[float]
) -> dict[str, list[tuple[Path, str]]]:
    total = len(all_images)

    if len(split_ratio) == 2:
        train_end = int(total * split_ratio[0])
        return {
            "train": all_images[:train_end],
            "val": all_images[train_end:],
        }

    # len == 3
    train_end = int(total * split_ratio[0])
    val_end = train_end + int(total * split_ratio[1])

    return {
        "train": all_images[:train_end],
        "val": all_images[train_end:val_end],
        "test": all_images[val_end:],
    }


def _write_splits(split_root: Path, splits: dict[str, list[tuple[Path, str]]]) -> None:
    """
    Compute train/val/(test) split boundaries.

    Parameters
    ----------
    all_images : list of tuple
        List of ``(Path, class_name)`` pairs.
    split_ratio : list of float
        Ratios that determine split sizes.

    Returns
    -------
    dict of str -> list
        Keys are ``"train"``, ``"val"``, and optionally ``"test"``.
        Values are lists of images belonging to each split.
    """
    for split_name, items in tqdm(splits.items(), desc="Creating splits"):
        # Create class folders
        for class_name in ["healthy", "unhealthy"]:
            (split_root / split_name / class_name).mkdir(parents=True, exist_ok=True)

        # Write files
        for src, class_name in items:
            dst = split_root / split_name / class_name / src.name
            dst.hardlink_to(src)
