"""Router de ejecución de scripts de herramientas."""
from fastapi import APIRouter, Query
from typing import Optional
from tools.script_runner import list_available_scripts, run_script, ScriptResult

router = APIRouter(prefix="/api/scripts-tools", tags=["scripts-tools"])


@router.get("/list")
def list_scripts() -> list[dict]:
    """Lista todos los scripts disponibles en la carpeta tools/."""
    return list_available_scripts()


@router.post("/run")
def execute_script(
    script: str = Query(..., description="Nombre del script a ejecutar"),
    args_str: Optional[str] = Query(None, description="Argumentos separados por comas"),
    timeout: int = Query(300, ge=1, le=3600, description="Timeout en segundos"),
    cwd: Optional[str] = Query(None, description="Directorio de trabajo"),
) -> dict:
    """
    Ejecuta un script desde la carpeta tools/.
    
    - **script**: Nombre del archivo del script (ej: "example.py")
    - **args_str**: Argumentos separados por comas (opcional)
    - **timeout**: Timeout en segundos (1-3600, por defecto 300)
    - **cwd**: Directorio de trabajo opcional
    """
    args = None
    if args_str:
        args = [a.strip() for a in args_str.split(",") if a.strip()]

    result: ScriptResult = run_script(
        script_name=script,
        args=args,
        timeout=timeout,
        cwd=cwd,
    )

    return {
        "script_name": result.script_name,
        "language": result.language,
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "return_code": result.return_code,
        "execution_time": round(result.execution_time, 3),
        "executed_at": result.executed_at.isoformat(),
        "error": result.error,
    }