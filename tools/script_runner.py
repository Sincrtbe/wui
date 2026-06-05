"""Servicio de ejecución de scripts desde la carpeta tools/."""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field


# Ruta base de la carpeta tools
TOOLS_DIR = Path(__file__).parent.resolve()

# Tipos de script soportados y sus extensiones
SUPPORTED_EXTENSIONS = {
    ".py": {"language": "python", "interpreter": sys.executable},
    ".bat": {"language": "batch", "interpreter": "cmd"},
    ".cmd": {"language": "batch", "interpreter": "cmd"},
    ".sh": {"language": "shell", "interpreter": "bash"},
    ".ps1": {"language": "powershell", "interpreter": "powershell"},
    ".js": {"language": "javascript", "interpreter": "node"},
    ".rb": {"language": "ruby", "interpreter": "ruby"},
}

# Timeout máximo en segundos para la ejecución
DEFAULT_TIMEOUT = 300


@dataclass
class ScriptResult:
    """Resultado de la ejecución de un script."""
    script_name: str
    language: str
    success: bool
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    execution_time: float = 0.0
    executed_at: datetime = field(default_factory=datetime.utcnow)
    error: str = ""


def list_available_scripts() -> list[dict]:
    """Lista todos los scripts disponibles en la carpeta tools/."""
    scripts = []
    if not TOOLS_DIR.exists():
        return scripts

    for file in sorted(TOOLS_DIR.iterdir()):
        if file.is_file() and file.suffix in SUPPORTED_EXTENSIONS:
            info = SUPPORTED_EXTENSIONS[file.suffix]
            scripts.append({
                "name": file.name,
                "path": str(file.relative_to(Path.cwd())),
                "language": info["language"],
                "size_bytes": file.stat().st_size,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
            })
    return scripts


def run_script(script_name: str, args: list[str] | None = None, timeout: int = DEFAULT_TIMEOUT, cwd: str | None = None) -> ScriptResult:
    """
    Ejecuta un script desde la carpeta tools/.
    
    Args:
        script_name: Nombre del archivo del script (ej: "example.py")
        args: Argumentos para pasar al script
        timeout: Timeout en segundos
        cwd: Directorio de trabajo (por defecto TOOLS_DIR)
    
    Returns:
        ScriptResult con el resultado de la ejecución
    """
    if not script_name:
        return ScriptResult(
            script_name="",
            language="unknown",
            success=False,
            error="El nombre del script es obligatorio",
        )

    script_path = TOOLS_DIR / script_name

    if not script_path.exists():
        return ScriptResult(
            script_name=script_name,
            language="unknown",
            success=False,
            error=f"Script no encontrado: {script_name}",
        )

    ext = script_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return ScriptResult(
            script_name=script_name,
            language="unknown",
            success=False,
            error=f"Tipo de script no soportado: {ext}. Tipos soportados: {', '.join(SUPPORTED_EXTENSIONS.keys())}",
        )

    lang_info = SUPPORTED_EXTENSIONS[ext]
    start_time = datetime.utcnow()

    try:
        if ext == ".py":
            cmd = [lang_info["interpreter"], str(script_path)]
        elif ext in (".bat", ".cmd"):
            cmd = [lang_info["interpreter"], "/c", str(script_path)]
        elif ext == ".sh":
            cmd = [lang_info["interpreter"], str(script_path)]
        elif ext == ".ps1":
            cmd = [lang_info["interpreter"], "-File", str(script_path)]
        elif ext == ".js":
            cmd = [lang_info["interpreter"], str(script_path)]
        elif ext == ".rb":
            cmd = [lang_info["interpreter"], str(script_path)]
        else:
            cmd = [str(script_path)]

        if args:
            cmd.extend(args)

        working_dir = Path(cwd) if cwd else TOOLS_DIR

        result = subprocess.run(
            cmd,
            cwd=str(working_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        end_time = datetime.utcnow()
        exec_time = (end_time - start_time).total_seconds()

        return ScriptResult(
            script_name=script_name,
            language=lang_info["language"],
            success=result.returncode == 0,
            stdout=result.stdout or "",
            stderr=result.stderr or "",
            return_code=result.returncode,
            execution_time=exec_time,
        )

    except subprocess.TimeoutExpired:
        end_time = datetime.utcnow()
        exec_time = (end_time - start_time).total_seconds()
        return ScriptResult(
            script_name=script_name,
            language=lang_info["language"],
            success=False,
            error=f"Timeout después de {timeout} segundos",
            execution_time=exec_time,
        )
    except FileNotFoundError:
        return ScriptResult(
            script_name=script_name,
            language=lang_info["language"],
            success=False,
            error=f"Interprete no encontrado: {lang_info['interpreter']}",
        )
    except Exception as e:
        end_time = datetime.utcnow()
        exec_time = (end_time - start_time).total_seconds()
        return ScriptResult(
            script_name=script_name,
            language=lang_info["language"],
            success=False,
            error=str(e),
            execution_time=exec_time,
        )