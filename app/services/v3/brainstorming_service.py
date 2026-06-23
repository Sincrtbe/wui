"""
app/services/v3/brainstorming_service.py
Genera lluvias de ideas para un canal usando el prompt de storming
y el topic del canal, creando UN ContentItem POR CADA IDEA.
El prompt debe devolver JSON estructurado con un array de ideas.
Cada idea se parsea y se guarda como content item individual en etapa "idea".
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
) -> list[dict]:
    """
    Genera una lluvia de ideas para un canal.
    1. Obtiene el canal → topic
    2. Obtiene el prompt de storming del sistema (category='storming')
    3. Llama al LLM con el topic + prompt
    4. Parsea la respuesta JSON — cada idea se guarda como content item individual
    5. Devuelve la lista de ContentItems creados
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
    storming_prompt = storming_prompts[0]

    # Renderizar: {{{tema}}} o {{topic}} según el schema del prompt
    content_template = storming_prompt["content"]
    prompt_content = content_template.replace("{{{tema}}}", topic)
    if prompt_content == content_template:
        prompt_content = content_template.replace("{{topic}}", topic)
    if prompt_content == content_template:
        prompt_content = content_template.replace("{{tema}}", topic)
    if prompt_content == content_template:
        prompt_content = content_template + f"\n\nTema: {topic}"

    messages = [{"role": "user", "content": prompt_content}]

    # Llamar al LLM
    from app.services.v3.llm_service import call_llm
    raw_result = call_llm(provider, messages, temperature=0.9, max_tokens=4096)

    # Parsear ideas
    ideas = _parse_ideas(raw_result)
    if not ideas:
        raise ValueError("No se pudieron parsear ideas de la respuesta del LLM.")

    # Crear UN content item por cada idea
    created = []
    timestamp = datetime.now(timezone.utc).isoformat()
    for idea in ideas:
        idea_title = idea.get("titulo") or idea.get("title") or idea.get("concepto", "Idea sin título")
        item = create_content_item(
            user_id=user_id,
            channel_id=channel_id,
            title=f"💡 {idea_title}",
            stage="idea",
            idea_notes=raw_result.strip(),
            structured_ideas=json.dumps(idea, ensure_ascii=False, indent=2),
        )
        created.append(item)

    return created
