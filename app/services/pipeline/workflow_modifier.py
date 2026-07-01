"""
workflow_modifier.py
Sistema de tags para workflows JSON de ComfyUI.
Adaptado de wan22_pipeline.py (forgotten-pantheons-studio).
Tags: {{{IMAGE_REF}}}, {{{IMG_PROMPT}}}, {{{VID_PROMPT}}}, {{{SEED}}}
"""

import json
from pathlib import Path
from typing import Dict, Any


class WorkflowModifier:
    """Modifica workflows JSON reemplazando tags {{{TAG_NAME}}}."""

    TAG_IMAGE_REF = "{{{IMAGE_REF}}}"
    TAG_IMG_PROMPT = "{{{IMG_PROMPT}}}"
    TAG_VID_PROMPT = "{{{VID_PROMPT}}}"
    TAG_SEED = "{{{SEED}}}"

    @staticmethod
    def _process_inputs(inputs: Any, tag_values: Dict[str, str]) -> Any:
        """Reemplaza tags en un objeto inputs (recursivo)."""
        if isinstance(inputs, dict):
            new = {}
            for k, v in inputs.items():
                if isinstance(v, str) and v in tag_values:
                    new[k] = tag_values[v]
                else:
                    new[k] = WorkflowModifier._process_inputs(v, tag_values)
            return new
        elif isinstance(inputs, list):
            return [WorkflowModifier._process_inputs(item, tag_values) for item in inputs]
        return inputs

    @classmethod
    def set_tags(cls, workflow: Dict, tag_values: Dict[str, str]) -> Dict:
        """Reemplaza todos los tags en el workflow."""
        return cls._process_inputs(workflow, tag_values)

    @classmethod
    def modify_image_workflow(
        cls,
        workflow_path: Path,
        image_ref: str,
        prompt: str,
        seed: int,
    ) -> Dict:
        """Carga el workflow de imagen y aplica los tags."""
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow = json.load(f)
        tag_values = {
            cls.TAG_IMAGE_REF: image_ref,
            cls.TAG_IMG_PROMPT: prompt,
            cls.TAG_SEED: str(seed),
        }
        return cls.set_tags(workflow, tag_values)

    @classmethod
    def modify_video_workflow(
        cls,
        workflow_path: Path,
        image_ref: str,
        prompt: str,
        seed: int,
    ) -> Dict:
        """Carga el workflow de video y aplica los tags."""
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow = json.load(f)
        tag_values = {
            cls.TAG_IMAGE_REF: image_ref,
            cls.TAG_VID_PROMPT: prompt,
            cls.TAG_SEED: str(seed),
        }
        return cls.set_tags(workflow, tag_values)
