"""
app/services/v3/brainstorming_service.py
Genera lluvias de ideas para un canal usando el prompt de storming
y el topic del canal, creando un ContentItem en etapa "idea".
"""

from typing import Optional
from app.core.multiuser_dal import create_content_item, get_channel
from app.services.v3.llm_service import call_llm, get_provider_config


def brainstorm_channel(
    user_id: str,
    channel_id: str,
    provider: str = "minimax",
    extra_topic: Optional[str] = None,
) -> dict:
    """
    Genera una lluvia de ideas para un canal.
    1. Obtiene el canal → topic
    2. Obtiene el prompt de storming del sistema
    3. Llama al LLM con el topic + prompt
    4. Crea un ContentItem en etapa "idea" con el resultado
    5. Devuelve el ContentItem creado
    """
    channel = get_channel(user_id, channel_id)
    if not channel:
        raise ValueError(f"Canal {channel_id} no encontrado.")

    topic = extra_topic or channel.get("topic", "")
    if not topic:
        raise ValueError("El canal no tiene un tema definido. Proporciona extra_topic o establece el topic del canal.")

    # Obtener prompt de storming del sistema
    from app.core.multiuser_dal import get_system_prompt
    storming_prompt = get_system_prompt("storming")
    if not storming_prompt:
        raise ValueError("Prompt de tormenta de ideas no encontrado en el sistema.")

    # Renderizar prompt con el topic
    prompt_content = storming_prompt["content"].replace("{{topic}}", topic)
    messages = [{"role": "user", "content": prompt_content}]

    # Llamar al LLM
    result = call_llm(provider, messages, temperature=0.9, max_tokens=2048)

    # Extraer ideas del resultado (devuelve texto libre; lo guardamos como idea_notes)
    # El resultado puede venir en markdown con "- idea" — lo guardamos tal cual
    ideas_text = result.strip()

    # Crear content item en etapa idea
    content = create_content_item(
        user_id=user_id,
        channel_id=channel_id,
        title=f"Lluvia de ideas: {topic}",
        stage="idea",
        idea_notes=ideas_text,
    )
    return content
