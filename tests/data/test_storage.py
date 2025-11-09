import os
from unittest.mock import MagicMock

import pytest

from lib.data.storage import HuggingFace, Storage


@pytest.fixture
def storage():
    storage = HuggingFace(token="fake-token")
    storage.api = MagicMock()
    return storage


def test_copy_file(storage, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("hello")
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    result = storage.copy_file_to_directory(source, target_dir, mode="copy")
    assert result.exists()
    assert result.read_text() == "hello"
    # Original file still exists
    assert source.exists()


def test_move_file(storage, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("hello")
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    result = storage.copy_file_to_directory(source, target_dir, mode="move")
    assert result.exists()
    assert result.read_text() == "hello"
    # Original file should not exist
    assert not source.exists()


def test_hardlink_file(storage, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("hello")
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    result = storage.copy_file_to_directory(source, target_dir, mode="hardlink")
    assert result.exists()
    assert result.read_text() == "hello"
    # Inode check to ensure hard link
    assert os.stat(source).st_ino == os.stat(result).st_ino


def test_override_false_raises(storage, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("hello")
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_file = target_dir / "source.txt"
    target_file.write_text("existing")

    # override=False should raise FileExistsError
    with pytest.raises(FileExistsError):
        storage.copy_file_to_directory(source, target_dir, mode="copy", override=False)

    # override=True should replace
    result = storage.copy_file_to_directory(source, target_dir, mode="copy", override=True)
    assert result.read_text() == "hello"


def test_invalid_mode(storage, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("hello")
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    with pytest.raises(ValueError):
        storage.copy_file_to_directory(source, target_dir, mode="invalid_mode")


def test_nonexistent_source(storage, tmp_path):
    source = tmp_path / "nonexistent.txt"
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    with pytest.raises(ValueError):
        storage.copy_file_to_directory(source, target_dir, mode="copy")


def test_nonexistent_target_dir_created(storage, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("hello")
    target_dir = tmp_path / "nonexistent_dir"

    # Should auto-create target_dir
    result = storage.copy_file_to_directory(source, target_dir, mode="copy")
    assert result.exists()
    assert target_dir.exists()


def test_validate_directory_success(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    returned = Storage.validate_directory(d)
    assert returned == d
    assert returned.exists() and returned.is_dir()


def test_validate_directory_nonexistent_raises(tmp_path):
    d = tmp_path / "does_not_exist"
    with pytest.raises(ValueError) as exc:
        Storage.validate_directory(d)
    assert "Provided directory does not exist" in str(exc.value)


def test_validate_directory_not_a_directory_raises(tmp_path):
    f = tmp_path / "not_a_dir.txt"
    f.write_text("content")
    with pytest.raises(ValueError) as exc:
        Storage.validate_directory(f)
    assert "Provided path is not a directory" in str(exc.value)


def test_save_calls_api_with_correct_params(storage, tmp_path):
    # Arrange
    test_dir = tmp_path / "data"
    test_dir.mkdir()
    test_file = test_dir / "file.txt"
    test_file.write_text("sample data")
    repo_id = "user/test-dataset"

    # Mock the API method
    storage.api.upload_file.return_value = "mocked_upload_result"

    # Act
    result = storage._save_file(test_file, repo_id)

    # Assert
    storage.api.upload_file.assert_called_once_with(
        path_or_fileobj=test_file,
        path_in_repo="/",
        repo_id=repo_id,
        repo_type="dataset",
    )
    assert result


def test_save_raises_if_no_file(storage):
    with pytest.raises(ValueError, match="Data must be either a Polars DataFrame or a file path."):
        storage.save(None, "user/test-dataset")


def test_save_raises_if_directory_does_not_exist(storage, tmp_path):
    non_existent = tmp_path / "nonexistent"
    with pytest.raises(ValueError, match="does not exist"):
        storage.save(non_existent, "user/test-dataset")
