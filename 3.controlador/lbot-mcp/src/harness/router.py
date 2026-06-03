import re
from typing import Literal

DIRECT_VERBS = r"(?:ande|v[áa]|gire|rode|vire|mova|recue|retroceda|avance|desloque)"
DIRECT_DIRS = r"(?:frente|tr[áa]s|atr[áa]s|esquerda|direita)"
COMPLEX_KEYWORDS = re.compile(
    r"(?:procure|encontre|ache|c[âa]mera|olhe|descreva|"
    r"tire\s+(?:uma\s+)?foto|aproxime-se|chegue\s+perto|"
    r"v[áa]\s+at[eé]\s+(?:o|a|um|uma)?\s*\w+|"
    r"o\s+que\s+h[áa]|qual\s+a\s+dist[âa]ncia|"
    r"me\s+diga|qual\s+[ée]\s+a|"
    r"identifique|reconhe[çc]a|localize|"
    r"centralize|alinhe|"
    r"objeto\s+(?:amarelo|azul|vermelho|verde|laranja|roxo)|"
    r"(?:esfera|cubo|cone|parede|alvo)\s+(?:amarelo|azul|vermelho|verde|laranja|roxo)?)",
    re.IGNORECASE,
)

AMBIGUOUS_PATTERNS = [
    (
        re.compile(r"\bquadrado\b", re.IGNORECASE),
        "ande 100 centímetros para frente, depois gire 90 graus para direita, "
        "ande 100 centímetros para frente, depois gire 90 graus para direita, "
        "ande 100 centímetros para frente, depois gire 90 graus para direita, "
        "ande 100 centímetros para frente, depois gire 90 graus para direita",
    ),
    (
        re.compile(r"\btri[âa]ngulo\b", re.IGNORECASE),
        "ande 100 centímetros para frente, depois gire 120 graus para direita, "
        "ande 100 centímetros para frente, depois gire 120 graus para direita, "
        "ande 100 centímetros para frente, depois gire 120 graus para direita",
    ),
    (
        re.compile(r"\bzig\s*zag\b", re.IGNORECASE),
        "ande 40 centímetros para frente, depois gire 45 graus para direita, "
        "ande 40 centímetros para frente, depois gire 90 graus para esquerda, "
        "ande 40 centímetros para frente, depois gire 45 graus para direita, "
        "ande 40 centímetros para frente",
    ),
]


_NUMBER_WORDS = re.compile(
    r"\b(?:um|dois|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|"
    r"quinze|vinte|trinta|quarenta|cinquenta|sessenta|setenta|oitenta|noventa|cem|mil)\b",
    re.IGNORECASE,
)


def classify_command(command: str) -> Literal["direct", "ambiguous", "complex"]:
    lowered = command.lower().strip()

    if COMPLEX_KEYWORDS.search(lowered):
        return "complex"

    for pattern, _ in AMBIGUOUS_PATTERNS:
        if pattern.search(lowered):
            return "ambiguous"

    has_verb = bool(re.search(DIRECT_VERBS, lowered))
    has_number = bool(re.search(r"\d", lowered)) or bool(_NUMBER_WORDS.search(lowered))
    has_dir = bool(re.search(DIRECT_DIRS, lowered))

    if has_verb and has_number and has_dir:
        return "direct"

    if re.search(
        r"\b(?:um pouco|devagar|pouco|mais ou menos|aproximadamente|metade|dobro)\b",
        lowered,
    ):
        return "ambiguous"

    return "complex"


def resolve_ambiguous(command: str) -> str | None:
    lowered = command.lower().strip()
    for pattern, resolved in AMBIGUOUS_PATTERNS:
        if pattern.search(lowered):
            return resolved
    return None
