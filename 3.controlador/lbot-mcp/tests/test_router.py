import pytest
from harness.router import classify_command, resolve_ambiguous


class TestClassifyCommand:
    def test_direct_simple_forward(self):
        assert classify_command("ande 30cm para frente") == "direct"

    def test_direct_rotate(self):
        assert classify_command("gire 90 graus para esquerda") == "direct"

    def test_direct_with_number_words(self):
        assert classify_command("ande quarenta centímetros para frente") == "direct"

    def test_direct_multiple_steps(self):
        assert (
            classify_command("ande 40cm para frente, depois vire 90 graus para direita")
            == "direct"
        )

    def test_ambiguous_zigzag(self):
        assert classify_command("anda em zig zag") == "ambiguous"

    def test_ambiguous_square(self):
        assert classify_command("faz um quadrado") == "ambiguous"

    def test_ambiguous_triangle(self):
        assert classify_command("ande em triângulo") == "ambiguous"

    def test_ambiguous_vague(self):
        assert classify_command("ande um pouco") == "ambiguous"

    def test_complex_search(self):
        assert classify_command("procure algo amarelo") == "complex"

    def test_complex_camera(self):
        assert classify_command("tire uma foto") == "complex"

    def test_complex_approach_object(self):
        assert classify_command("vá até o objeto azul") == "complex"

    def test_complex_describe(self):
        assert classify_command("descreva o que você vê") == "complex"

    def test_complex_fallback_when_no_pattern(self):
        assert classify_command("olá") == "complex"


class TestResolveAmbiguous:
    def test_resolve_square(self):
        resolved = resolve_ambiguous("faz um quadrado")
        assert resolved is not None
        assert "ande 100 centímetros para frente" in resolved
        assert "gire 90 graus para direita" in resolved

    def test_resolve_triangle(self):
        resolved = resolve_ambiguous("ande em triângulo")
        assert resolved is not None
        assert "gire 120 graus para direita" in resolved

    def test_resolve_zigzag(self):
        resolved = resolve_ambiguous("anda em zig zag")
        assert resolved is not None
        assert "gire 45 graus para direita" in resolved
        assert "gire 90 graus para esquerda" in resolved

    def test_resolve_unknown_returns_none(self):
        assert resolve_ambiguous("ande um pouco") is None
