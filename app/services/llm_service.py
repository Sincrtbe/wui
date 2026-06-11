"""Servicio de integración con LLM para generación de contenido."""
import os
import json
from sqlalchemy.orm import Session
from app.models.config import GlobalConfig


class LLMService:
    """Servicio para interactuar con LLM configurado (OpenAI, local, etc.)."""

    @staticmethod
    def get_llm_config(db: Session) -> dict:
        """Obtiene la configuración del LLM desde la BD."""
        url_config = db.query(GlobalConfig).filter(GlobalConfig.key == "llm_url").first()
        key_config = db.query(GlobalConfig).filter(GlobalConfig.key == "llm_key").first()
        
        return {
            "url": url_config.value if url_config else "https://api.openai.com/v1",
            "key": key_config.value if key_config else os.getenv("OPENAI_API_KEY", "")
        }

    @staticmethod
    def generate_script_from_idea(db: Session, idea_title: str, idea_notes: str) -> dict:
        """Genera un guion a partir de una idea usando LLM."""
        try:
            from openai import OpenAI
            
            config = LLMService.get_llm_config(db)
            
            client = OpenAI(api_key=config["key"], base_url=config["url"])
            
            prompt = f"""Basándote en la siguiente idea de contenido, genera un guión profesional para un vídeo.

**Idea:** {idea_title}
**Descripción:** {idea_notes}

Por favor, proporciona:
1. Un guión de voz detallado (lo que se dirá en el vídeo)
2. Un artículo o descripción complementaria

Formato de respuesta JSON:
{{
    "script_content": "...",
    "article_content": "..."
}}
"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en creación de contenido multimedia."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            result_text = response.choices[0].message.content
            
            # Intentar parsear JSON
            try:
                result = json.loads(result_text)
            except:
                # Si no es JSON válido, dividir por secciones
                result = {
                    "script_content": result_text,
                    "article_content": ""
                }
            
            return {
                "success": True,
                "data": result
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def generate_seo_metadata(db: Session, title: str, content: str) -> dict:
        """Genera metadatos SEO (tags, descripción) para un vídeo."""
        try:
            from openai import OpenAI
            
            config = LLMService.get_llm_config(db)
            client = OpenAI(api_key=config["key"], base_url=config["url"])
            
            prompt = f"""Analiza el siguiente contenido y genera metadatos SEO optimizados para YouTube:

**Título:** {title}
**Contenido:** {content[:500]}...

Proporciona:
1. Tags relevantes (máximo 10)
2. Descripción optimizada (máximo 500 caracteres)
3. Palabras clave principales

Formato JSON:
{{
    "tags": [...],
    "description": "...",
    "keywords": [...]
}}
"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en SEO y optimización de contenido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            result_text = response.choices[0].message.content
            
            try:
                result = json.loads(result_text)
            except:
                result = {"tags": [], "description": title, "keywords": []}
            
            return {
                "success": True,
                "data": result
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
