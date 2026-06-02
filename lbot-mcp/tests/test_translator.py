import pytest
import os


MODEL_AVAILABLE = False
_translator_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "lbot-natural-language-controller", "lbot-v7",
)
_model_path = os.path.join(_translator_dir, "lbot_translator_v7.pt")
if os.path.exists(_model_path):
    MODEL_AVAILABLE = True


@pytest.mark.skipif(not MODEL_AVAILABLE, reason="Modelo .pt nao encontrado")
class TestTranslatorWrapperWithModel:
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        from mcp_server.translator import TranslatorWrapper

        TranslatorWrapper._instance = None
        yield
        TranslatorWrapper._instance = None

    @pytest.fixture
    def translator(self):
        from mcp_server.translator import TranslatorWrapper

        return TranslatorWrapper()

    def test_loads_model(self, translator):
        assert not translator.is_loaded()
        translator._ensure_loaded()
        assert translator.is_loaded()

    def test_singleton_reuses_instance(self):
        from mcp_server.translator import TranslatorWrapper

        t1 = TranslatorWrapper()
        t2 = TranslatorWrapper()
        assert t1 is t2

    def test_translate_simple_forward(self, translator):
        translator._ensure_loaded()
        result = translator.translate("ande 40 centimetros para frente")
        assert "D" in result
        assert len(result) > 2

    def test_translate_rotation(self, translator):
        translator._ensure_loaded()
        result = translator.translate("vire 90 graus para direita")
        assert "R" in result or "D" in result
        assert len(result) > 2

    def test_translate_verbose(self, translator):
        translator._ensure_loaded()
        original, preprocessed, lbml = translator.translate_verbose("ande 30cm para frente")
        assert isinstance(original, str)
        assert isinstance(preprocessed, str)
        assert isinstance(lbml, str)
        assert len(lbml) > 0

    def test_translate_invalid_input(self, translator):
        translator._ensure_loaded()
        with pytest.raises(Exception):
            translator.translate("zzzzzzzzzzzzzzzzzzz")

    def test_loaded_flag_works(self, translator):
        if not translator.is_loaded():
            translator.translate("ande 1cm para frente")
        assert translator.is_loaded()


class TestTranslatorWrapperErrors:
    def test_unavailable_model_detected(self, tmp_path):
        from mcp_server.translator import TranslatorWrapper, TranslationError

        TranslatorWrapper._instance = None
        wrapper = TranslatorWrapper()

        original_path = os.path.join(_translator_dir, "lbot_translator_v7.pt")
        if not os.path.exists(original_path):
            pytest.skip("Modelo original nao existe para teste de renomeacao")

        backup_path = os.path.join(_translator_dir, "_backup_model_xyz.pt")
        try:
            os.rename(original_path, backup_path)

            with pytest.raises(TranslationError, match=r"Modelo n.o encontrado"):
                wrapper._ensure_loaded()
        finally:
            os.rename(backup_path, original_path)
            TranslatorWrapper._instance = None

    def test_translation_error_is_exception(self):
        from mcp_server.translator import TranslationError

        err = TranslationError("teste")
        assert isinstance(err, Exception)
