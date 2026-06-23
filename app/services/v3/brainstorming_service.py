"""
app/services/v3/brainstorming_service.py
Genera lluvias de ideas para un canal usando el prompt de storming
y el topic del canal, creando un ContentItem en etapa "idea".
El prompt debe devolver JSON estructurado. El resultado se parsea y se guarda
como texto raw (idea_notes) + estructura parseada (structured_ideas).
"""

import json
import re
from typing import Optional
from app.core.multiuser_dal import (
    create_content_item,
    get_channel,
    list_system_prompts,
)


def _parse_ideas(raw_text: str) -> list[dict]:
    """
    Extrae el bloque JSON del texto devuelto por el LLM.
    Busca entre ```json ... ``` o usa el texto directamente.
    """
    # Intentar extraer bloque markdown
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Buscar el primer { y el último }
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = raw_text[start:end+1]
        else:
            json_str = raw_text.strip()

    try:
        data = json.loads(json_str)
        # Normalizar: puede venir como {"ideas": [...]} o directamente [...]
        ideas = data.get("ideas", data if isinstance(data, list) else [])
        return ideas
    except json.JSONDecodeError:
        return []


def brainstorm_channel(
    user_id: str,
    channel_id: str,
    provider: str = "minimax",
    extra_topic: Optional[str] = None,
) -> dict:
    """
    Genera una lluvia de ideas para un canal.
    1. Obtiene el canal → topic
    2. Obtiene el prompt de storming del sistema (category='storming')
    3. Llama al LLM con el topic + prompt
    4. Parsea la respuesta JSON y guarda en structured_ideas
    5. Crea un ContentItem en etapa "idea" con el resultado
    6. Devuelve el ContentItem creado
    """
    channel = get_channel(user_id, channel_id)
    if not channel:
        raise ValueError(f"Canal {channel_id} no encontrado.")

    topic = extra_topic or channel.get("topic", "")
    if not topic:
        raise ValueError(
            "El canal no tiene un tema definido. "
            "Proporciona extra_topic o establece el topic del canal."
        )

    # Obtener prompt de storming (por categoría)
    storming_prompts = list_system_prompts(category="storming")
    if not storming_prompts:
        raise ValueError("No hay prompts de storming en el sistema.")
    storming_prompt = storming_prompts[0]  # Primer prompt de storming

    # Renderizar: {{{tema}}} o {{topic}} según el schema del prompt
    content_template = storming_prompt["content"]
    # Intentar ambas variantes
    prompt_content = content_template.replace("{{{tema}}}", topic)
    if prompt_content == content_template:
        prompt_content = content_template.replace("{{topic}}", topic)
    if prompt_content == content_template:
        prompt_content = content_template.replace("{{tema}}", topic)
    # Si no encontró ninguna marca, concatenar
    if prompt_content == content_template:
        prompt_content = content_template + f"\n\nTema: {topic}"

    messages = [{"role": "user", "content": prompt_content}]

    # Llamar al LLM
    from app.services.v3.llm_service import call_llm
    raw_result = call_llm(provider, messages, temperature=0.9, max_tokens=2048)

    # Parsear ideas
    ideas = _parse_ideas(raw_result)
    structured_ideas = json.dumps(ideas, ensure_ascii=False)

    # Crear content item en etapa idea
    content = create_content_item(
        user_id=user_id,
        channel_id=channel_id,
        title=f"Lluvia de ideas: {topic}",
        stage="idea",
        idea_notes=raw_result.strip(),
        structured_ideas=structured_ideas,
    )
    return content
