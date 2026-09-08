import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.design_generation.storage import delete_generated_image


class DeleteGeneratedImageTests(unittest.TestCase):
    def test_deletes_file_inside_storage_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = Path(directory)
            image = storage / "slide.png"
            image.write_bytes(b"image")
            with patch("app.design_generation.storage.STORAGE_DIR", storage):
                delete_generated_image("/media/design-drafts/slide.png")
            self.assertFalse(image.exists())

    def test_does_not_delete_file_outside_storage_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            storage = root / "storage"
            storage.mkdir()
            outside = root / "outside.png"
            outside.write_bytes(b"keep")
            with patch("app.design_generation.storage.STORAGE_DIR", storage):
                delete_generated_image("/media/design-drafts/../outside.png")
            self.assertTrue(outside.exists())


if __name__ == "__main__":
    unittest.main()
