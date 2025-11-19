from lib.data.utils import splitter


def test_comput_splots(tmp_path):
    # Create a temporary dataset structure

    all_images = [
        (tmp_path / f"image_{i}.jpg", "healthy" if i % 2 == 0 else "unhealthy") for i in range(20)
    ]

    # Perform the split
    split_ratio = [0.7, 0.2, 0.1]
    splits = splitter._compute_splits(all_images, split_ratio)

    # Check the number of files in each split
    assert len(splits["train"]) == 14  # 70% of 20 files
    assert len(splits["val"]) == 4  # 20% of 20 files
    assert len(splits["test"]) == 2  # 10% of 20 files


def test_load_images(tmp_path):
    # Create a temporary dataset structure
    healthy_dir = tmp_path / "healthy"
    unhealthy_dir = tmp_path / "unhealthy"
    healthy_dir.mkdir()
    unhealthy_dir.mkdir()

    # Create some dummy image files
    for i in range(5):
        (healthy_dir / f"healthy_image_{i}.jpg").write_text("dummy data")
        (unhealthy_dir / f"unhealthy_image_{i}.jpg").write_text("dummy data")

    # Load images
    all_images = splitter._load_images(tmp_path)

    # Check that all images are loaded with correct labels
    assert len(all_images) == 10
    healthy_images = [img for img, label in all_images if label == "healthy"]
    unhealthy_images = [img for img, label in all_images if label == "unhealthy"]

    assert len(healthy_images) == 5
    assert len(unhealthy_images) == 5


def test_create_split_root(tmp_path):
    destination = tmp_path

    split_root = splitter._create_split_root(destination)

    assert split_root.exists()
    assert split_root.is_dir()
    assert split_root.name == destination.name


def test_write_splits(tmp_path):
    # Create a temporary dataset structure
    split_root = tmp_path / "3_split"
    split_root.mkdir()

    splits = {
        "train": [(tmp_path / "image_1.jpg", "healthy"), (tmp_path / "image_2.jpg", "unhealthy")],
        "val": [(tmp_path / "image_3.jpg", "healthy")],
        "test": [(tmp_path / "image_4.jpg", "unhealthy")],
    }

    for split_name, images in splits.items():
        for image_path, class_name in images:
            image_path.write_text("dummy data")  # Create dummy image files

    # Write splits
    splitter._write_splits(split_root, splits)

    # Check that files are written in the correct structure
    for split_name, images in splits.items():
        for image_path, class_name in images:
            dest_path = split_root / split_name / class_name / image_path.name
            assert dest_path.exists()
            assert dest_path.is_file()
            assert dest_path.read_text() == "dummy data"  # Assuming dummy data was written


def test_validate_split_ratio():
    # Valid ratios
    splitter._validate_split_ratio([0.8, 0.2])
    splitter._validate_split_ratio([0.7, 0.2, 0.1])

    # Invalid ratios
    try:
        splitter._validate_split_ratio([0.5, 0.6])
    except ValueError as e:
        assert str(e) == "Split ratios must sum to 1.0, but sum to 1.1"

    try:
        splitter._validate_split_ratio([0.5, 0.1, 0.1, 0.3])
    except ValueError as e:
        assert str(e) == "Split ratio must have length 2 or 3, but got length 4"
