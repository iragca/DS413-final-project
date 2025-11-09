from loguru import logger
from tqdm import tqdm
import typer

from lib.data.storage import HuggingFace

app = typer.Typer()


@app.command()
def main():
    logger.info("Downloading datasets...")

    datasets = [flood_control_dataset]

    for dataset_func in datasets:
        with tqdm(total=1, desc=dataset_func.__name__) as pbar:
            dataset_func()
            pbar.update(1)

    logger.success("Downloading datasets complete.")


def flood_control_dataset():
    storage = HuggingFace()
    data_path = storage.load(
        repo_id="chrisandrei/DPWH_Flood_Control_2018-2025_Projects",
        filename="flood-control-projects-visual_2025-11-08.csv",
    )
    logger.info(f"Flood control dataset saved to: {data_path}")
    return data_path


if __name__ == "__main__":
    app()
