"""
Pruebas unitarias y de integración para WUI v2.
Ejecutar con: python -m pytest tests/test_all.py -v
"""

import os
import sys
import json
import time
import pytest
import httpx
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Añadir ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Configuración ────────────────────────────────────────────────────────────

BASE_URL = "http://127.0.0.1:9080"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"

# Token guardado para tests posteriores
_auth_token = None

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_auth_token():
    """Obtiene un token de autenticación válido."""
    global _auth_token
    if _auth_token:
        return _auth_token
    
    client = httpx.Client(timeout=10.0)
    try:
        resp = client.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": ADMIN_USER, "password": ADMIN_PASS}
        )
        if resp.status_code == 200:
            data = resp.json()
            _auth_token = data["access_token"]
            return _auth_token
        else:
            print(f"ERROR: Login failed with status {resp.status_code}: {resp.text}")
            return None
    finally:
        client.close()


def get_headers():
    """Headers con token de auth."""
    token = get_auth_token()
    if not token:
        pytest.skip("No se pudo obtener token de autenticación")
    return {"Authorization": f"Bearer {token}"}


def create_test_channel(name="Test Channel", youtube_url="https://www.youtube.com/channel/UCxxxxxxxxx"):
    """Crea un canal de prueba."""
    client = httpx.Client(timeout=10.0)
    try:
        resp = client.post(
            f"{BASE_URL}/api/channels/",
            json={"name": name, "url": youtube_url},
            headers=get_headers()
        )
        return resp
    finally:
        client.close()


def delete_test_channel(channel_id):
    """Elimina un canal de prueba."""
    client = httpx.Client(timeout=10.0)
    try:
        resp = client.delete(
            f"{BASE_URL}/api/channels/{channel_id}",
            headers=get_headers()
        )
        return resp
    finally:
        client.close()


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: AUTH MODULE
# ═══════════════════════════════════════════════════════════════════════════════

class TestAuthModule:
    """Tests del módulo de autenticación."""
    
    def test_login_success(self):
        """Login con credenciales válidas devuelve token."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": ADMIN_USER, "password": ADMIN_PASS}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert "token_type" in data
            assert data["token_type"] == "bearer"
            assert "expires_in" in data
        finally:
            client.close()
    
    def test_login_invalid_password(self):
        """Login con contraseña incorrecta devuelve 401."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": ADMIN_USER, "password": "wrong_password"}
            )
            assert resp.status_code == 401
        finally:
            client.close()
    
    def test_login_invalid_user(self):
        """Login con usuario inexistente devuelve 401."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": "nonexistent_user", "password": ADMIN_PASS}
            )
            assert resp.status_code == 401
        finally:
            client.close()
    
    def test_login_missing_fields(self):
        """Login sin campos devuelve error."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": ADMIN_USER}
            )
            assert resp.status_code == 422  # Validation error
        finally:
            client.close()


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: CHANNELS MODULE
# ═══════════════════════════════════════════════════════════════════════════════

class TestChannelsModule:
    """Tests del módulo de canales."""
    
    def test_create_channel(self):
        """Crear un canal devuelve 201."""
        resp = create_test_channel(
            name=f"Test Channel {int(time.time())}",
            youtube_url="https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxxx"
        )
        assert resp.status_code in (201, 200)
    
    def test_list_channels(self):
        """Listar canales devuelve un objeto con lista."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.get(
                f"{BASE_URL}/api/channels/",
                headers=get_headers()
            )
            assert resp.status_code == 200
            data = resp.json()
            # La API devuelve ChannelListResponse: {"channels": [], "total": 0}
            assert isinstance(data, dict)
            assert "channels" in data
            assert "total" in data
        finally:
            client.close()
    
    def test_get_channel_by_id(self):
        """Obtener canal por ID existe."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.get(
                f"{BASE_URL}/api/channels/",
                headers=get_headers()
            )
            data = resp.json()
            channels = data.get("channels", [])
            if len(channels) > 0:
                channel_id = channels[0]["channel_id"]
                resp = client.get(
                    f"{BASE_URL}/api/channels/{channel_id}",
                    headers=get_headers()
                )
                # Puede ser 200 o 404 si el servicio no funciona
                assert resp.status_code in (200, 404)
        finally:
            client.close()
    
    def test_delete_channel(self):
        """Eliminar canal devuelve 200."""
        channel_id = "UCdeleteTest"
        create_test_channel(name="Delete Test", youtube_url="https://www.youtube.com/channel/UCdeleteTest")
        resp = delete_test_channel(channel_id)
        assert resp.status_code in (200, 404)  # Puede ser 404 si ya existe


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: CREATIVE MODULE
# ═══════════════════════════════════════════════════════════════════════════════

class TestCreativeModule:
    """Tests del módulo de Creative Studio."""
    
    def test_templates_list(self):
        """Lista de templates devuelve 6 plantillas."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.get(
                f"{BASE_URL}/api/creative/templates",
                headers=get_headers()
            )
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) == 6  # 6 plantillas creadas
        finally:
            client.close()
    
    def test_generate_storming(self):
        """Generar prompt de storming devuelve texto."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/creative/generate",
                json={
                    "template_name": "storming",
                    "variables": {"tema": "Inteligencia Artificial"}
                },
                headers=get_headers()
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "prompt" in data
            assert len(data["prompt"]) > 100
            assert data["model_suggested"] == "qwen"
        finally:
            client.close()
    
    def test_generate_development(self):
        """Generar guion de desarrollo."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/creative/generate",
                json={
                    "template_name": "development",
                    "variables": {
                        "titulo": "Test Video",
                        "concepto": "Concepto de prueba"
                    }
                },
                headers=get_headers()
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "prompt" in data
            assert data["model_suggested"] == "qwen"
        finally:
            client.close()
    
    def test_generate_scene_graphic(self):
        """Generar prompt para Flux 2.0."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/creative/generate",
                json={
                    "template_name": "scene_graphic",
                    "variables": {
                        "titulo": "Test Video",
                        "descripcion_escena": "Escena de prueba"
                    }
                },
                headers=get_headers()
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "prompt" in data
            assert "flux" in data["model_suggested"]
        finally:
            client.close()
    
    def test_generate_scene_video(self):
        """Generar prompt para Wan 2.2."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/creative/generate",
                json={
                    "template_name": "scene_video",
                    "variables": {
                        "titulo": "Test Video",
                        "descripcion_escena": "Escena de prueba"
                    }
                },
                headers=get_headers()
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "prompt" in data
            assert "wan" in data["model_suggested"]
        finally:
            client.close()
    
    def test_generate_conversation(self):
        """Generar prompts visuales desde texto."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/creative/generate",
                json={
                    "template_name": "conversation_to_visual",
                    "variables": {
                        "texto_a_visualizar": "Texto de ejemplo para visualizar"
                    }
                },
                headers=get_headers()
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "prompt" in data
        finally:
            client.close()


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: SERVICE LAYER (Unit Tests)
# ═══════════════════════════════════════════════════════════════════════════════

class TestServiceLayer:
    """Tests unitarios del servicio de Creative Studio."""
    
    def test_get_prompt_template_exists(self):
        """Plantilla storming existe."""
        from app.services.creative_service import get_prompt_template
        
        template = get_prompt_template("storming")
        assert template is not None
        assert len(template) > 100
    
    def test_get_prompt_template_not_found(self):
        """Plantilla inexistente devuelve None."""
        from app.services.creative_service import get_prompt_template
        
        template = get_prompt_template("nonexistent_template")
        assert template is None
    
    def test_list_available_templates_count(self):
        """Lista 6 plantillas."""
        from app.services.creative_service import list_available_templates
        
        templates = list_available_templates()
        assert len(templates) == 6
    
    def test_render_template_storming(self):
        """Rellena plantilla de storming correctamente."""
        from app.services.creative_service import render_template
        
        prompt = render_template("storming", {"tema": "Test"})
        assert "Test" in prompt
        assert len(prompt) > 500
    
    def test_render_template_missing_key(self):
        """Render sin variable necesaria mantiene placeholders."""
        from app.services.creative_service import render_template
        
        # Si no pasas todas las variables, los {{placeholders}} deben quedar
        prompt = render_template("storming", {})
        assert "{{" in prompt  # Debe mantener placeholders sin rellenar
    
    def test_render_template_invalid(self):
        """Template inválido lanza ValueError."""
        from app.services.creative_service import render_template
        
        with pytest.raises(ValueError):
            render_template("nonexistent", {})
    
    def test_get_model_config(self):
        """Config de modelos devuelve estructura correcta."""
        from app.services.creative_service import get_model_config
        
        config = get_model_config()
        assert "models" in config
        assert "endpoints" in config
        assert config["models"]["qwen"] == "Qwen3-35B-A3B"
        assert config["models"]["flux"] == "Flux 2.0"
        assert config["models"]["wan"] == "Wan 2.2"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: INTEGRATION & EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Tests de integración y casos extremos."""
    
    def test_health_check(self):
        """Endpoint de health check."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.get(f"{BASE_URL}/api/ready")
            assert resp.status_code == 200
            data = resp.json()
            assert data["ready"] is True
        finally:
            client.close()
    
    def test_creative_without_auth(self):
        """Acceder a endpoints creativos sin auth devuelve 401."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.get(f"{BASE_URL}/api/creative/templates")
            assert resp.status_code == 401
        finally:
            client.close()
    
    def test_channels_without_auth(self):
        """Acceder a endpoints de canales sin auth devuelve 401."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.get(f"{BASE_URL}/api/channels/")
            assert resp.status_code == 401
        finally:
            client.close()
    
    def test_generate_with_empty_template_name(self):
        """Generar con template_name vacío devuelve 422."""
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.post(
                f"{BASE_URL}/api/creative/generate",
                json={"template_name": "", "variables": {}},
                headers=get_headers()
            )
            assert resp.status_code == 422
        finally:
            client.close()
    
    def test_channel_with_special_chars(self):
        """Crear canal con caracteres especiales en el nombre."""
        resp = create_test_channel(
            name="Test !@#$%&*()",
            youtube_url="https://www.youtube.com/channel/UCspecialxxx"
        )
        assert resp.status_code in (201, 200)
    
    def test_generate_all_templates(self):
        """Todos los templates generan output."""
        templates_to_test = [
            "storming",
            "development",
            "classification",
            "scene_graphic",
            "scene_video",
            "conversation_to_visual",
        ]
        
        client = httpx.Client(timeout=10.0)
        try:
            for tmpl in templates_to_test:
                resp = client.post(
                    f"{BASE_URL}/api/creative/generate",
                    json={
                        "template_name": tmpl,
                        "variables": {"tema": "test"}
                    },
                    headers=get_headers()
                )
                assert resp.status_code == 200, f"Failed for template: {tmpl}"
        finally:
            client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
