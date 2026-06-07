import logging

logger = logging.getLogger(__name__)


def build_vision_message(image_base64: str, description: str) -> dict:
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": (
                    "Analise esta imagem da camera frontal do robo. "
                    "A camera do robo nao e de muita qualidade, "
                    "nao seja excessivamente detalhista na analise. "
                    "Ha um(a) \"" + description + "\" visivel nesta imagem? "
                    "O objeto pode estar ao fundo, parcialmente visivel, "
                    "distante ou parcialmente obstruido. "
                    "Responda APENAS com \"SIM\" ou \"NAO\"."
                ),
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/png;base64," + image_base64,
                },
            },
        ],
    }


async def ask_llm_if_object_visible(
    client, model: str, image_base64: str, description: str
) -> bool:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[build_vision_message(image_base64, description)],
            max_tokens=5,
            temperature=0.0,
        )
        answer = response.choices[0].message.content.strip().upper()
        logger.info("LLM vision response for '%s': %s", description, answer)
        return "SIM" in answer
    except Exception as e:
        logger.warning("LLM vision query failed for '%s': %s", description, e)
        return False
