from pathlib import Path, PosixPath

from faker import Faker
import pytest
import torch
from torchvision import transforms

from lib.data import CombinedMegaPlantDataset, MegaPlantDataset, UnhealthyMegaPlantDataset


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


@pytest.fixture
def unhealthy_dataset(tmp_path) -> UnhealthyMegaPlantDataset:
    # Setup: create a temporary unhealthy dataset structure
    class_dir = Path(tmp_path / "unhealthy")
    class_dir.mkdir(parents=True, exist_ok=True)

    for symptom in UnhealthyMegaPlantDataset(tmp_path).SYMPTOM_MAP.keys():
        symptom_dir = class_dir / symptom
        symptom_dir.mkdir(parents=True, exist_ok=True)
        for i in range(5):  # Create 5 dummy files per symptom
            file_path = symptom_dir / f"image_{i}.jpg"
            with open(file_path, "wb") as f:
                f.write(Faker().image(size=(100, 100)))

    return UnhealthyMegaPlantDataset(data_path=tmp_path)


@pytest.fixture
def combined_dataset(tmp_path) -> CombinedMegaPlantDataset:
    # Setup: create a temporary combined dataset structure
    # Healthy images
    healthy_dir = Path(tmp_path / "healthy")
    healthy_dir.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        file_path = healthy_dir / f"image_{i}.jpg"
        with open(file_path, "wb") as f:
            f.write(Faker().image(size=(100, 100)))

    # Unhealthy images
    unhealthy_dir = Path(tmp_path / "unhealthy")
    unhealthy_dir.mkdir(parents=True, exist_ok=True)
    for symptom in UnhealthyMegaPlantDataset(tmp_path).SYMPTOM_MAP.keys():
        symptom_dir = unhealthy_dir / symptom
        symptom_dir.mkdir(parents=True, exist_ok=True)
        for i in range(5):
            file_path = symptom_dir / f"image_{i}.jpg"
            with open(file_path, "wb") as f:
                f.write(Faker().image(size=(100, 100)))

    return CombinedMegaPlantDataset(data_path=tmp_path)


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


def test_unhealthy_dataset_length(unhealthy_dataset: UnhealthyMegaPlantDataset):
    assert len(unhealthy_dataset) == 60  # Only unhealthy samples


def test_unhealthy_dataset_getitem(unhealthy_dataset: UnhealthyMegaPlantDataset):
    for i in range(len(unhealthy_dataset)):
        image_path, label = unhealthy_dataset[i]
        assert type(image_path) in {Path, PosixPath}
        assert label in unhealthy_dataset.SYMPTOM_MAP.values()  # Check symptom labels


def test_combined_dataset_length(combined_dataset: CombinedMegaPlantDataset):
    assert len(combined_dataset) == 65  # 5 healthy + 60 unhealthy


def test_combined_dataset_getitem(combined_dataset: CombinedMegaPlantDataset):
    for i in range(len(combined_dataset)):
        image_path, label = combined_dataset[i]
        assert type(image_path) in {Path, PosixPath}
        assert label in combined_dataset.CLASS_MAP.values()  # Check all class labels
