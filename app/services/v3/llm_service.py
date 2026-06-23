"""
app/services/v3/llm_service.py
Servicio unificado para llamar a LLMs (Minimax, OpenAI, etc.)
con formato de petición/respuesta estructurado para WUI.

Esquemática:
  - build_request()   → construye el payload según el provider
  - parse_response()   → extrae el texto de la respuesta según el provider
  - call()             → llamada HTTP genérica con reintentos y errores
"""

import json
import time
from typing import Optional
from datetime import datetime, timezone
from app.services.v3.config_service import get_api_credential


PROVIDER_DEFAULTS = {
    "minimax": {
        "name": "Minimax",
        "base_url": "https://api.minimax.io/anthropic/v1",
        "model": "MiniMax-M2.7",
        "max_tokens": 2048,
        "timeout": 120,
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "max_tokens": 2048,
        "timeout": 60,
    },
    "elevenlabs": {
        "name": "ElevenLabs",
        "base_url": "https://api.elevenlabs.io/v1",
        "model": None,
        "max_tokens": 1024,
        "timeout": 30,
    },
    "minimax_tts": {
        "name": "Minimax TTS",
        "base_url": "https://api.minimax.chat/v1",
        "model": "speech-01",
        "max_tokens": 1024,
        "timeout": 30,
    },
    "comfyui": {
        "name": "ComfyUI",
        "base_url": "http://localhost:8188",
        "model": None,
        "max_tokens": 1024,
        "timeout": 120,
    },
    "flux": {
        "name": "Flux",
        "base_url": "https://api.replicate.com/v1",
        "model": "black-forest-labs/flux-1-schnell",
        "max_tokens": 512,
        "timeout": 60,
    },
}


def get_provider_config(provider: str) -> dict:
    """Fusiona defaults + credenciales guardadas del usuario."""
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    cfg = {**defaults}
    api_key = get_api_credential(provider, "api_key")
    base_url = get_api_credential(provider, "base_url")
    model = get_api_credential(provider, "model")
    enabled = get_api_credential(provider, "enabled")
    if enabled:
        if api_key:
            cfg["api_key"] = api_key
        if base_url:
            cfg["base_url"] = base_url
        if model:
            cfg["model"] = model
    return cfg


def _build_minimax_payload(model: str, messages: list, temperature: float, max_tokens: int) -> dict:
    # Anthropic-compatible API: usa max_output_tokens
    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }


def _build_openai_payload(model: str, messages: list, temperature: float, max_tokens: int) -> dict:
    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def _call_http(base_url: str, path: str, headers: dict, json_payload: dict, timeout: int) -> dict:
    import httpx
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=json_payload, headers=headers)
        response.raise_for_status()
        return response.json()


def call_llm(
    provider: str,
    messages: list,
    temperature: float = 0.8,
    max_tokens: Optional[int] = None,
    retry: int = 2,
) -> str:
    """
    Llamada genérica a un LLM. Devuelve el texto de la respuesta.
    """
    cfg = get_provider_config(provider)
    api_key = cfg.get("api_key")
    if not api_key:
        raise PermissionError(f"API '{provider}' no configurada o no habilitada.")

    base_url = cfg["base_url"]
    model = cfg["model"]
    timeout = cfg.get("timeout", 60)
    max_tokens = max_tokens or cfg.get("max_tokens", 2048)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if provider == "minimax":
        payload = _build_minimax_payload(model, messages, temperature, max_tokens)
        path = "messages"
    elif provider == "openai":
        payload = _build_openai_payload(model, messages, temperature, max_tokens)
        path = "chat/completions"
    else:
        raise ValueError(f"Provider '{provider}' no soportado aún.")

    last_err = None
    for attempt in range(retry + 1):
        try:
            data = _call_http(base_url, path, headers, payload, timeout)
            if provider == "minimax":
                content_list = data.get("content", [])
                for block in content_list:
                    if block.get("type") == "text":
                        return block["text"]
                raise RuntimeError(f"Respuesta sin texto: {data}")
            elif provider == "openai":
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            if attempt < retry:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Error tras {retry+1} intentos: {last_err}")
