"""Router para la gestión de biblioteca de prompts basada en archivos JSON."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from app.services.prompt_service import PromptService

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


# ========== Pydantic Models ==========

class PromptCreate(BaseModel):
    title: str
    content: str
    category: str = "otro"
    description: Optional[str] = None
    prompt_type: Optional[str] = None


class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class CategoryCreate(BaseModel):
    name: str


class CategoryDelete(BaseModel):
    name: str


class RatePromptRequest(BaseModel):
    rating: float


class UsePromptRequest(BaseModel):
    variables: dict


class PromptSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None


# ========== Responses ==========

class PromptResponse(BaseModel):
    id: float
    title: str
    content: str
    category: str
    prompt_type: Optional[str]
    description: Optional[str]
    variables: list[str]
    rating: float
    usage_count: int
    version: int
    is_active: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    name: str
    prompt_count: int


class CategoriesListResponse(BaseModel):
    categories: list[dict]


class DeleteResponse(BaseModel):
    success: bool
    message: str


# ========== Routes: Categories ==========

@router.get("/categories", response_model=CategoriesListResponse)
def list_categories():
    """Obtiene todas las categorías con el conteo de prompts."""
    categories = PromptService.get_categories()
    result = []
    for cat in categories:
        prompts = PromptService.get_all_prompts(category=cat)
        result.append({
            "name": cat,
            "prompt_count": len(prompts)
        })
    return {"categories": result}


@router.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate):
    """Crea una nueva categoría (subcarpeta)."""
    cat_name = category.name.strip().lower().replace(" ", "_").replace("-", "_")
    if not cat_name:
        raise HTTPException(status_code=400, detail="El nombre de la categoría no puede estar vacío")

    PromptService.ensure_category(cat_name)
    prompts = PromptService.get_all_prompts(category=cat_name)
    return {"name": cat_name, "prompt_count": len(prompts)}


@router.delete("/categories", response_model=DeleteResponse)
def delete_category(category: CategoryDelete):
    """Elimina una categoría y todos sus prompts."""
    cat_name = category.name.strip().lower().replace(" ", "_").replace("-", "_")
    if not cat_name:
        raise HTTPException(status_code=400, detail="El nombre de la categoría no puede estar vacío")

    success = PromptService.delete_category(cat_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Categoría no encontrada: {cat_name}")

    return {"success": True, "message": f"Categoría '{cat_name}' eliminada"}


# ========== Routes: Prompts ==========

@router.post("/", response_model=PromptResponse)
def create_prompt(prompt: PromptCreate):
    """Crea un nuevo prompt."""
    if not prompt.title or not prompt.content:
        raise HTTPException(status_code=400, detail="title y content son obligatorios")

    try:
        result = PromptService.create_prompt(
            title=prompt.title,
            content=prompt.content,
            category=prompt.category,
            description=prompt.description,
            prompt_type=prompt.prompt_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear prompt: {str(e)}")


@router.get("/")
def list_prompts(
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    search: Optional[str] = Query(None, description="Buscar en título, descripción y contenido"),
):
    """Lista todos los prompts, opcionalmente filtrados por categoría."""
    prompts = PromptService.get_all_prompts(category=category)

    if search:
        prompts = PromptService.search_prompts(query=search, category=category)

    return prompts


@router.get("/search")
def search_prompts(query: str = Query(..., min_length=1), category: Optional[str] = None):
    """Busca prompts por título, descripción o contenido."""
    results = PromptService.search_prompts(query=query, category=category)
    return results


@router.get("/categories/{category}/files")
def list_category_files(category: str):
    """Lista los archivos JSON de una categoría."""
    all_prompts = PromptService.get_all_prompts(category=category)
    return [
        {
            "filename": p.get("id", ""),
            "title": p.get("title", ""),
            "created_at": p.get("created_at", "")
        }
        for p in all_prompts
    ]


@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt(prompt_id: str):
    """Obtiene un prompt específico por su ID."""
    prompt = PromptService.get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return prompt


@router.patch("/{category}/{filename}", response_model=PromptResponse)
def update_prompt(
    category: str,
    filename: str,
    prompt: PromptUpdate
):
    """Actualiza un prompt existente (por categoría y filename)."""
    current = PromptService.get_prompt_by_filename(category, filename)
    if not current:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")

    try:
        result = PromptService.update_prompt(
            category=category,
            filename=filename,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            new_category=prompt.category
        )
        if not result:
            raise HTTPException(status_code=404, detail="Prompt no encontrado")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar prompt: {str(e)}")


@router.patch("/by-id/{prompt_id}", response_model=PromptResponse)
def update_prompt_by_id(
    prompt_id: str,
    prompt: PromptUpdate
):
    """Actualiza un prompt existente por su ID (timestamp)."""
    current = PromptService.get_prompt_by_id(prompt_id)
    if not current:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")

    category = current.get("category", "otro")
    # Generar filename a partir del título
    filename = PromptService.generate_filename(prompt.title if prompt.title else current["title"])

    try:
        result = PromptService.update_prompt(
            category=category,
            filename=filename,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            new_category=prompt.category
        )
        if not result:
            raise HTTPException(status_code=404, detail="Prompt no encontrado")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar prompt: {str(e)}")


@router.post("/{prompt_id}/rate")
def rate_prompt(prompt_id: str, rating_data: RatePromptRequest):
    """Califica un prompt (0-5)."""
    if rating_data.rating < 0 or rating_data.rating > 5:
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 0 y 5")

    result = PromptService.rate_prompt(prompt_id, rating_data.rating)
    if not result:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return result


@router.post("/{prompt_id}/use", response_model=dict)
def use_prompt(prompt_id: str, req: UsePromptRequest):
    """Usa un prompt sustituyendo sus variables."""
    prompt = PromptService.get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")

    # Validar variables
    validation = PromptService.validate_variables(prompt["content"], req.variables)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Variables faltantes: {validation['missing']}"
        )

    # Sustituir variables
    final_content = PromptService.substitute_variables(prompt["content"], req.variables)

    # Incrementar contador de uso
    PromptService.increment_usage(prompt_id)

    return {
        "prompt_id": prompt_id,
        "title": prompt["title"],
        "original_content": prompt["content"],
        "final_content": final_content,
        "variables_used": req.variables
    }


@router.delete("/{category}/{filename}", response_model=DeleteResponse)
def delete_prompt(category: str, filename: str):
    """Elimina un prompt (por categoría y filename)."""
    success = PromptService.delete_prompt(category, filename)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return {"success": True, "message": "Prompt eliminado"}


@router.delete("/by-id/{prompt_id}", response_model=DeleteResponse)
def delete_prompt_by_id(prompt_id: str):
    """Elimina un prompt por su ID (timestamp)."""
    prompt = PromptService.get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")

    category = prompt.get("category", "otro")
    # El filename se puede inferir del título
    filename = PromptService.generate_filename(prompt["title"])
    success = PromptService.delete_prompt(category, filename)
    if not success:
        # Intentar también con el ID como filename (formato timestamp)
        success = PromptService.delete_prompt(category, f"{prompt_id}.json")
    if not success:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return {"success": True, "message": "Prompt eliminado"}


@router.post("/{prompt_id}/validate")
def validate_prompt_variables(prompt_id: str, variables: dict):
    """Valida que todas las variables requeridas estén proporcionadas."""
    prompt = PromptService.get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")

    validation = PromptService.validate_variables(prompt["content"], variables)
    return validation