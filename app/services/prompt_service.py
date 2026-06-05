"""Servicio de gestión de prompts y variables."""
import re
from sqlalchemy.orm import Session
from app.models.prompt import Prompt


class PromptService:
    """Servicio para gestionar prompts reutilizables."""

    @staticmethod
    def extract_variables(content: str) -> list[str]:
        """Extrae las variables de un prompt (formato {{variable}})."""
        pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(pattern, content)
        return list(set(matches))  # Eliminar duplicados

    @staticmethod
    def substitute_variables(content: str, variables: dict) -> str:
        """Sustituye las variables en un prompt con los valores proporcionados."""
        result = content
        for key, value in variables.items():
            pattern = r'\{\{' + key + r'\}\}'
            result = re.sub(pattern, str(value), result)
        return result

    @staticmethod
    def validate_variables(content: str, provided_vars: dict) -> dict:
        """Valida que todas las variables requeridas estén proporcionadas."""
        required = PromptService.extract_variables(content)
        provided = set(provided_vars.keys())
        
        missing = set(required) - provided
        extra = provided - set(required)
        
        return {
            "valid": len(missing) == 0,
            "required": required,
            "missing": list(missing),
            "extra": list(extra)
        }

    @staticmethod
    def create_prompt(
        db: Session,
        title: str,
        content: str,
        prompt_type: str,
        description: str = None,
        meta_data: dict = None
    ) -> Prompt:
        """Crea un nuevo prompt."""
        variables = PromptService.extract_variables(content)
        
        prompt = Prompt(
            title=title,
            content=content,
            prompt_type=prompt_type,
            description=description,
            variables=variables,
            meta_data=meta_data or {}
        )
        
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    def get_all_prompts(db: Session, prompt_type: str = None, is_active: str = "active") -> list[Prompt]:
        """Obtiene todos los prompts, opcionalmente filtrados por tipo."""
        query = db.query(Prompt).filter(Prompt.is_active == is_active)
        
        if prompt_type:
            query = query.filter(Prompt.prompt_type == prompt_type)
        
        return query.order_by(Prompt.rating.desc(), Prompt.usage_count.desc()).all()

    @staticmethod
    def get_prompt_by_id(db: Session, prompt_id: int) -> Prompt:
        """Obtiene un prompt por ID."""
        return db.query(Prompt).filter(Prompt.id == prompt_id).first()

    @staticmethod
    def update_prompt(
        db: Session,
        prompt_id: int,
        title: str = None,
        content: str = None,
        description: str = None,
        rating: float = None
    ) -> Prompt:
        """Actualiza un prompt."""
        prompt = PromptService.get_prompt_by_id(db, prompt_id)
        if not prompt:
            return None
        
        if title:
            prompt.title = title
        if content:
            prompt.content = content
            prompt.variables = PromptService.extract_variables(content)
            prompt.version += 1
        if description is not None:
            prompt.description = description
        if rating is not None:
            prompt.rating = max(0, min(5, rating))  # Limitar entre 0 y 5
        
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    def rate_prompt(db: Session, prompt_id: int, rating: float) -> Prompt:
        """Califica un prompt."""
        prompt = PromptService.get_prompt_by_id(db, prompt_id)
        if not prompt:
            return None
        
        # Promediar con la calificación anterior
        if prompt.rating > 0:
            prompt.rating = (prompt.rating + rating) / 2
        else:
            prompt.rating = rating
        
        prompt.rating = max(0, min(5, prompt.rating))
        
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    def increment_usage(db: Session, prompt_id: int) -> Prompt:
        """Incrementa el contador de uso de un prompt."""
        prompt = PromptService.get_prompt_by_id(db, prompt_id)
        if not prompt:
            return None
        
        prompt.usage_count += 1
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    def delete_prompt(db: Session, prompt_id: int) -> bool:
        """Marca un prompt como inactivo (soft delete)."""
        prompt = PromptService.get_prompt_by_id(db, prompt_id)
        if not prompt:
            return False
        
        prompt.is_active = "inactive"
        db.commit()
        return True

    @staticmethod
    def get_top_prompts(db: Session, limit: int = 10) -> list[Prompt]:
        """Obtiene los prompts mejor puntuados."""
        return db.query(Prompt)\
            .filter(Prompt.is_active == "active")\
            .order_by(Prompt.rating.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def search_prompts(db: Session, query: str) -> list[Prompt]:
        """Busca prompts por título o descripción."""
        return db.query(Prompt)\
            .filter(Prompt.is_active == "active")\
            .filter((Prompt.title.ilike(f"%{query}%")) | (Prompt.description.ilike(f"%{query}%")))\
            .all()
