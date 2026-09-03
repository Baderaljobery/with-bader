import unittest

from app.design_generation.templates import (
    TEMPLATE_IDS,
    TemplateReferenceNotFoundError,
    load_template_reference_images,
)


class DesignTemplatesTests(unittest.TestCase):
    def test_all_registered_templates_resolve_to_real_files(self):
        self.assertEqual(len(TEMPLATE_IDS), 4)
        for template_id in TEMPLATE_IDS:
            images = load_template_reference_images(template_id)
            self.assertGreaterEqual(len(images), 1)
            for data, mime_type in images:
                self.assertGreater(len(data), 1000)
                self.assertIn(mime_type, ("image/png", "image/jpeg", "image/webp"))

    def test_unknown_template_raises(self):
        with self.assertRaises(TemplateReferenceNotFoundError):
            load_template_reference_images("template-does-not-exist")

    def test_path_traversal_template_id_is_rejected(self):
        with self.assertRaises(TemplateReferenceNotFoundError):
            load_template_reference_images("../../etc")


if __name__ == "__main__":
    unittest.main()
