from lib.data.utils import Deduplicator


def test_hash_file(tmp_path):
    # Create a temporary file with known content
    file_content = b"Test content for hashing."
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_bytes(file_content)

    # Compute the hash using the Deduplicator
    computed_hash = Deduplicator.hash_file(temp_file)

    # Precomputed MD5 hash for the given content
    # This expected hash was precomputed using md5sum command line tool
    expected_hash = "281806b4919a3accdd2ddbebbe7372e9"

    assert computed_hash == expected_hash


def test_get_files(tmp_path):
    # Create a temporary directory structure
    (tmp_path / "subdir").mkdir()
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "subdir" / "file2.txt"
    file1.write_text("File 1 content")
    file2.write_text("File 2 content")

    # Get all files using Deduplicator
    all_files = Deduplicator.get_files(tmp_path)

    # Check that both files are found
    assert set(all_files) == {file1, file2}


def test_deduplicate_folder_keep_first(tmp_path):
    # Create duplicate files
    content = b"Duplicate content"
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file3 = tmp_path / "file3.txt"
    file1.write_bytes(content)
    file2.write_bytes(content)
    file3.write_bytes(b"Unique content")

    deduplicator = Deduplicator()
    deduplicator.deduplicate_folder(tmp_path, strategy="keep_first")

    # After deduplication, only one of the duplicate files should remain
    remaining_files = Deduplicator.get_files(tmp_path)
    remaining_file_names = [f.name for f in remaining_files]

    assert "file1.txt" in remaining_file_names
    assert "file2.txt" not in remaining_file_names
    assert "file3.txt" in remaining_file_names
    assert len(remaining_files) == 2  # One duplicate removed


def test_deduplicate_folder_keep_last(tmp_path):
    # Create duplicate files
    content = b"Duplicate content"
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file1.write_bytes(content)
    file2.write_bytes(content)

    deduplicator = Deduplicator()
    deduplicator.deduplicate_folder(tmp_path, strategy="keep_last")

    # After deduplication, only the last duplicate file should remain
    remaining_files = Deduplicator.get_files(tmp_path)
    remaining_file_names = [f.name for f in remaining_files]

    assert "file1.txt" not in remaining_file_names
    assert "file2.txt" in remaining_file_names
    assert len(remaining_files) == 1  # One duplicate removed