import kagglehub
import questionary
from tqdm import tqdm

from lib.config import logger
from lib.data.storage import HuggingFace

from .base_menu import BaseMenu


class DownloadDatasetMenu(BaseMenu):
    def menu(self) -> None:
        datasets = {
            dataset.__name__: dataset
            for dataset in [
                flood_control_dataset,
                plant_doc_dataset,
                plantvillage_dataset,
                diamos_dataset,
                megaplant_dataset,
            ]
        }

        chosen_datasets = questionary.checkbox(
            "Select datasets to download:",
            choices=[dataset_name for dataset_name in datasets],
        ).ask()

        if not chosen_datasets:
            return

        logger.info("Downloading datasets...")

        pbar = tqdm(total=len(chosen_datasets))
        for dataset_name in chosen_datasets:
            pbar.set_description(f"Downloading {dataset_name}")
            datasets[dataset_name]()
            pbar.update(1)

        logger.success("Downloading datasets complete.")

    @property
    def name(self) -> str:
        return "Download Dataset"


def flood_control_dataset():
    """
    Download the flood control dataset from Hugging Face.
    Dataset source: https://bettergov.ph/flood-control-projects
    """
    storage = HuggingFace()
    data_path = storage.load(
        repo_id="chrisandrei/DPWH_Flood_Control_2018-2025_Projects",
        filename="flood-control-projects-visual_2025-11-08.csv",
    )
    logger.info(f"Flood control dataset saved to: {data_path}")
    return data_path


def plant_doc_dataset():
    """
    Download the PlantDoc dataset from Hugging Face.
    Dataset source: https://www.kaggle.com/datasets/nirmalsankalana/plantdoc-dataset
    """
    # Download latest version
    path = kagglehub.dataset_download("nirmalsankalana/plantdoc-dataset")

    print("Path to dataset files:", path)
    return path


def plantvillage_dataset():
    """
    Download the PlantVillage dataset from Kaggle.
    Dataset source: https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset
    """
    # Download latest version
    path = kagglehub.dataset_download("abdallahalidev/plantvillage-dataset")
    print("Path to dataset files:", path)
    return path


def diamos_dataset():
    """
    Download the DiaMOS dataset from Kaggle.
    Dataset source: https://huggingface.co/datasets/chrisandrei/diamos
    """
    storage = HuggingFace()
    data_path = storage.load(
        repo_id="chrisandrei/diamos",
        filename="leaves.zip",
    )
    logger.info(f"DiaMOS dataset saved to: {data_path}")
    return data_path


def megaplant_dataset():
    """
    Compiled images of various plant datasets.
    Download the Processed Dataset from Hugging Face.
    Dataset source: https://huggingface.co/datasets/chrisandrei/MegaPlant
    """
    storage = HuggingFace()
    data_path = storage.load(
        repo_id="chrisandrei/MegaPlant",
        filename="leaves.zip",
    )
    logger.info(f"Processed dataset saved to: {data_path}")
    return data_path
