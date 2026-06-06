from ..server import mcp
from ..context import get_translator
from ..translator import TranslationError


@mcp.tool()
async def translate(command: str) -> str:
    """Traduz um comando em linguagem natural para LBML (LBot Markup Language).
    
    Args:
        command: Comando em linguagem natural (ex: "ande 30cm para frente")
    
    Returns:
        String LBML (ex: "D30F;") ou "ERRO" se a traducao falhar.
    """
    try:
        translator = get_translator()
        return translator.translate(command)
    except TranslationError:
        return "ERRO"
