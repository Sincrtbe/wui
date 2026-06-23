"""
app/services/v3/brainstorming_service.py
Genera lluvias de ideas para un canal usando el prompt de storming
y guarda TODAS las ideas generadas en UN SOLO content item.
"""

import json
import re
from datetime import datetime, timezone
from typing import Optional
from app.core.multiuser_dal import (
    create_content_item,
    get_channel,
    list_system_prompts,
)


def _parse_ideas(raw_text: str) -> list[dict]:
    """
    Extrae el bloque JSON del texto devuelto por el LLM.
    """
    # Buscar bloque markdown ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = raw_text[start:end+1]
        else:
            json_str = raw_text.strip()

    try:
        data = json.loads(json_str)
        ideas = data.get("ideas", data if isinstance(data, list) else [])
        return ideas if isinstance(ideas, list) else []
    except json.JSONDecodeError:
        return []


def brainstorm_channel(
    user_id: str,
    channel_id: str,
    provider: str = "minimax",
    extra_topic: Optional[str] = None,
) -> list[dict]:
    """
    Genera una lluvia de ideas para un canal.
    1. Obtiene el canal → topic
    2. Obtiene el prompt de storming (category='storming')
    3. Llama al LLM
    4. Parsea la respuesta JSON
    5. Guarda TODAS las ideas en UN SOLO content item con:
       - title: "Lluvia de ideas: <topic>"
       - structured_ideas: lista completa de dicts de ideas
       - idea_notes: JSON original del LLM (raw)
    6. Devuelve el content item creado
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

    # Prompt de storming
    storming_prompts = list_system_prompts(category="storming")
    if not storming_prompts:
        raise ValueError("No hay prompts de storming en el sistema.")
    storming_prompt = storming_prompts[0]

    content_template = storming_prompt["content"]
    prompt_content = content_template.replace("{{{tema}}}", topic)
    if prompt_content == content_template:
        prompt_content = content_template.replace("{{topic}}", topic)
    if prompt_content == content_template:
        prompt_content = content_template.replace("{{tema}}", topic)
    if prompt_content == content_template:
        prompt_content = content_template + f"\n\nTema: {topic}"

    messages = [{"role": "user", "content": prompt_content}]

    from app.services.v3.llm_service import call_llm
    raw_result = call_llm(provider, messages, temperature=0.9, max_tokens=4096)

    ideas = _parse_ideas(raw_result)
    if not ideas:
        raise ValueError("No se pudieron parsear ideas de la respuesta del LLM.")

    # Guardar TODAS las ideas en UN solo content item
    item = create_content_item(
        user_id=user_id,
        channel_id=channel_id,
        title=f"💡 Lluvia de ideas: {topic}",
        stage="idea",
        idea_notes=raw_result.strip(),
        structured_ideas=json.dumps(ideas, ensure_ascii=False, indent=2),
    )
    return [item]
