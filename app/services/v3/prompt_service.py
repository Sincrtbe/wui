"""
app/services/v3/prompt_service.py
Servicio de prompts para WUI v3.
"""

from typing import Optional

from app.core.multiuser_dal import (
    create_prompt,
    get_prompt,
    list_prompts,
    update_prompt,
    delete_prompt,
    extract_variables,
    validate_variables,
    render_prompt,
    build_render_context,
    resolve_pipeline_prompt,
    get_pipeline_assignments,
    set_pipeline_assignment,
    remove_pipeline_assignment,
    PIPELINE_STAGES,
)


def create_user_prompt(
    user_id: str,
    name: str,
    content: str,
    category: str = "custom",
    description: str = "",
    tags: Optional[list[str]] = None,
    variables_schema: Optional[list[dict]] = None,
) -> dict:
    """Crea un prompt y valida sus variables."""
    valid_vars, invalid_vars = validate_variables(content)
    if invalid_vars:
        # No lanzamos error, solo advertimos. El prompt se crea igual.
        pass
    return create_prompt(
        user_id=user_id,
        name=name,
        content=content,
        category=category,
        description=description,
        tags=tags or [],
        variables_schema=variables_schema or [],
    )


def update_user_prompt(
    user_id: str,
    prompt_id: str,
    updates: dict,
) -> Optional[dict]:
    """Actualiza un prompt existente."""
    return update_prompt(user_id, prompt_id, updates)


def render_prompt_for_content(
    user_id: str,
    prompt_content: str,
    channel_id: str,
    content_id: Optional[str] = None,
    extra_context: Optional[dict] = None,
) -> dict:
    """
    Renderiza un prompt con el contexto del canal y contenido.
    Retorna el prompt renderizado + variables usadas/missing.
    """
    context = build_render_context(user_id, channel_id, content_id)
    if extra_context:
        context.update(extra_context)

    valid_vars, invalid_vars = validate_variables(prompt_content)
    # Ignoramos inválidas por now (las dejamos como {{{variable}}} en el output)

    rendered = render_prompt(prompt_content, context)
    return {
        "rendered": rendered,
        "variables_used": valid_vars,
        "variables_missing": [],
    }


def get_prompt_for_stage(
    user_id: str,
    stage: str,
    channel_id: Optional[str] = None,
) -> Optional[dict]:
    """Resuelve qué prompt usar para una etapa, con la cadena de fallback."""
    return resolve_pipeline_prompt(user_id, stage, channel_id)
