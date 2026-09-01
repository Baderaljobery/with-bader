import unittest


class ExtractorFactoryTests(unittest.TestCase):
    def test_mock_provider_returns_mock_extractor(self):
        from app.core.config import settings
        from app.research.extraction.factory import build_research_extractor
        from app.research.extraction.mock import MockResearchExtractor

        original = settings.research_extractor_provider
        settings.research_extractor_provider = "mock"
        try:
            extractor = build_research_extractor()
            self.assertIsInstance(extractor, MockResearchExtractor)
        finally:
            settings.research_extractor_provider = original

    def test_unknown_provider_raises_configuration_error(self):
        from app.core.config import settings
        from app.research.extraction.base import ResearchExtractorConfigurationError
        from app.research.extraction.factory import build_research_extractor

        original = settings.research_extractor_provider
        settings.research_extractor_provider = "openai"
        try:
            with self.assertRaises(ResearchExtractorConfigurationError):
                build_research_extractor()
        finally:
            settings.research_extractor_provider = original

    def test_research_engine_uses_factory_not_hardcoded_mock(self):
        import inspect

        from app.research import research_engine

        source = inspect.getsource(research_engine.get_research_engine)
        self.assertIn("build_research_extractor()", source)
        self.assertNotIn("MockResearchExtractor()", source)


if __name__ == "__main__":
    unittest.main()
