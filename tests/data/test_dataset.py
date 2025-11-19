from pathlib import Path, PosixPath

from faker import Faker
import pytest
import torch
from torchvision import transforms

from lib.data import MegaPlantDataset


@pytest.fixture
def dataset(tmp_path) -> MegaPlantDataset:
    # Setup: create a temporary dataset structure
    class_names = ["healthy", "unhealthy"]
    faker = Faker()
    for class_name in class_names:
        class_dir = Path(tmp_path / class_name)
        class_dir.mkdir(parents=True, exist_ok=True)
        for i in range(5):  # Create 5 dummy files per class
            file_path = class_dir / f"image_{i}.jpg"
            with open(file_path, "wb") as f:
                f.write(faker.image(size=(100, 100)))

    return MegaPlantDataset(data_path=tmp_path)


def test_dataset_length(dataset: MegaPlantDataset):
    assert len(dataset) == 10  # 5 healthy + 5 unhealthy


def test_dataset_getitem(dataset: MegaPlantDataset):
    for i in range(len(dataset)):
        image_path, label = dataset[i]
        assert type(image_path) in {Path, PosixPath}
        assert label in {0, 1}  # 0 for healthy, 1 for unhealthy


def test_dataset_transforms(tmp_path):
    # Define a simple transform
    simple_transform = transforms.Compose(
        [
            transforms.Resize((64, 64)),
            transforms.ToTensor(),
        ]
    )

    class_names = ["healthy", "unhealthy"]
    faker = Faker()
    for class_name in class_names:
        class_dir = Path(tmp_path / class_name)
        class_dir.mkdir(parents=True, exist_ok=True)
        for i in range(5):  # Create 5 dummy files per class
            file_path = class_dir / f"image_{i}.jpg"
            with open(file_path, "wb") as f:
                f.write(faker.image(size=(100, 100)))

    # Create a new dataset instance with transforms
    transformed_dataset = MegaPlantDataset(data_path=tmp_path, transforms=simple_transform)

    for i in range(len(transformed_dataset)):
        image, label = transformed_dataset[i]
        assert isinstance(image, torch.Tensor)
        assert image.shape == (3, 64, 64)  # Check transformed image shape
        assert label in {0, 1}  # 0 for healthy, 1 for unhealthy
