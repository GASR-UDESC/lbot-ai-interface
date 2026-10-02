import pytest

from mcp_server.services.movement import expected_lbml, translate_and_move

from .fake_backend import FakeBackend


class Translator:
    def __init__(self, output):
        self.output = output

    def translate(self, _):
        return self.output


@pytest.mark.parametrize(
    "text",
    [
        "não ande 20 cm para frente",
        "ande 30 cm para esquerda",
        "vire 20 graus para frente",
        "ande 0 cm para frente",
        "ande 999 cm para frente",
    ],
)
def test_unsupported_or_ambiguous_moves_rejected(text):
    with pytest.raises(ValueError):
        expected_lbml(text)


@pytest.mark.asyncio
async def test_translation_mismatch_cannot_actuate():
    b = FakeBackend()
    r = await translate_and_move(b, Translator("D40F;"), "ande 30 cm para frente")
    assert r["reason"] == "translation_mismatch"
    assert b.commands == []


@pytest.mark.asyncio
async def test_numeric_movement_is_segmented_and_confirmed():
    b = FakeBackend()
    r = await translate_and_move(
        b,
        Translator("D30F;R90L;"),
        "ande 30 cm para frente, depois vire 90 graus para esquerda",
    )
    assert r["status"] == "completed"
    assert b.commands == ["D20F;", "D10F;", "R45L;", "R45L;"]
    assert r["distance_cm"] == 30


@pytest.mark.asyncio
async def test_blocked_move_is_reported_without_actuating():
    b = FakeBackend()
    b.distance = 25
    r = await translate_and_move(b, Translator("D20F;"), "ande 20 cm para frente")
    assert r["status"] == "blocked"
    assert not b.commands
