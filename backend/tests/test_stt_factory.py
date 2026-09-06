import unittest


class STTFactoryTests(unittest.TestCase):
    def test_factory_resolves_groq(self):
        from app.audio.factory import build_stt_provider
        from app.audio.providers.groq import GroqWhisperSTTProvider
        from app.core.config import settings

        original_provider = settings.stt_provider
        original_key = settings.groq_api_key
        settings.stt_provider = "groq"
        settings.groq_api_key = "fake-key"
        try:
            provider = build_stt_provider()
            self.assertIsInstance(provider, GroqWhisperSTTProvider)
            self.assertEqual(provider.provider_name, "groq")
        finally:
            settings.stt_provider = original_provider
            settings.groq_api_key = original_key

    def test_cohere_is_no_longer_a_supported_provider(self):
        """Cohere STT was fully removed (2026-09-06, Groq Whisper
        migration) - "cohere" must now fail exactly like any other unknown
        provider name, not silently resolve to anything."""
        from app.audio.base import STTProviderConfigurationError
        from app.audio.factory import build_stt_provider
        from app.core.config import settings

        original_provider = settings.stt_provider
        settings.stt_provider = "cohere"
        try:
            with self.assertRaises(STTProviderConfigurationError):
                build_stt_provider()
        finally:
            settings.stt_provider = original_provider

    def test_cohere_provider_module_no_longer_exists(self):
        with self.assertRaises(ModuleNotFoundError):
            import app.audio.providers.cohere  # noqa: F401

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

    def test_missing_groq_key_fails_clearly(self):
        from app.audio.base import STTProviderConfigurationError
        from app.audio.factory import build_stt_provider
        from app.core.config import settings

        original_provider = settings.stt_provider
        original_key = settings.groq_api_key
        settings.stt_provider = "groq"
        settings.groq_api_key = None
        try:
            with self.assertRaises(STTProviderConfigurationError):
                build_stt_provider()
        finally:
            settings.stt_provider = original_provider
            settings.groq_api_key = original_key

    def test_provider_and_model_configurable_via_settings(self):
        from app.audio.factory import build_stt_provider
        from app.core.config import settings

        original_provider = settings.stt_provider
        original_key = settings.groq_api_key
        original_model = settings.groq_stt_model
        settings.stt_provider = "groq"
        settings.groq_api_key = "fake-key"
        settings.groq_stt_model = "whisper-large-v3-turbo"
        try:
            provider = build_stt_provider()
            self.assertEqual(provider.model_name, "whisper-large-v3-turbo")
        finally:
            settings.stt_provider = original_provider
            settings.groq_api_key = original_key
            settings.groq_stt_model = original_model

    def test_default_language_configurable_via_settings(self):
        from app.audio.factory import build_stt_provider
        from app.core.config import settings

        original_provider = settings.stt_provider
        original_key = settings.groq_api_key
        original_language = settings.groq_stt_language
        settings.stt_provider = "groq"
        settings.groq_api_key = "fake-key"
        settings.groq_stt_language = "en"
        try:
            provider = build_stt_provider()
            self.assertEqual(provider._default_language, "en")
        finally:
            settings.stt_provider = original_provider
            settings.groq_api_key = original_key
            settings.groq_stt_language = original_language


if __name__ == "__main__":
    unittest.main()
