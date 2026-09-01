import unittest


class STTFactoryTests(unittest.TestCase):
    def test_factory_resolves_cohere(self):
        from app.audio.factory import build_stt_provider
        from app.audio.providers.cohere import CohereSTTProvider
        from app.core.config import settings

        original_provider = settings.stt_provider
        original_key = settings.cohere_api_key
        settings.stt_provider = "cohere"
        settings.cohere_api_key = "fake-key"
        try:
            provider = build_stt_provider()
            self.assertIsInstance(provider, CohereSTTProvider)
            self.assertEqual(provider.provider_name, "cohere")
        finally:
            settings.stt_provider = original_provider
            settings.cohere_api_key = original_key

    def test_unknown_provider_errors_cleanly(self):
        from app.audio.base import STTProviderConfigurationError
        from app.audio.factory import build_stt_provider
        from app.core.config import settings

        original_provider = settings.stt_provider
        settings.stt_provider = "deepgram"
        try:
            with self.assertRaises(STTProviderConfigurationError):
                build_stt_provider()
        finally:
            settings.stt_provider = original_provider

    def test_missing_cohere_key_fails_clearly(self):
        from app.audio.base import STTProviderConfigurationError
        from app.audio.factory import build_stt_provider
        from app.core.config import settings

        original_provider = settings.stt_provider
        original_key = settings.cohere_api_key
        settings.stt_provider = "cohere"
        settings.cohere_api_key = None
        try:
            with self.assertRaises(STTProviderConfigurationError):
                build_stt_provider()
        finally:
            settings.stt_provider = original_provider
            settings.cohere_api_key = original_key

    def test_provider_and_model_configurable_via_settings(self):
        from app.audio.factory import build_stt_provider
        from app.core.config import settings

        original_provider = settings.stt_provider
        original_key = settings.cohere_api_key
        original_model = settings.cohere_stt_model
        settings.stt_provider = "cohere"
        settings.cohere_api_key = "fake-key"
        settings.cohere_stt_model = "some-future-model"
        try:
            provider = build_stt_provider()
            self.assertEqual(provider.model_name, "some-future-model")
        finally:
            settings.stt_provider = original_provider
            settings.cohere_api_key = original_key
            settings.cohere_stt_model = original_model


if __name__ == "__main__":
    unittest.main()
