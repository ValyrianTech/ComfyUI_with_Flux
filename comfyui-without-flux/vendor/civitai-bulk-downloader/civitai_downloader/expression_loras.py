"""
AutoExpress expression LoRAs, one set per base model type

The list mirrors autoexpress_core/resources/expression_loras.json in AutoExpress.
"""

import json
from importlib import resources
from typing import Dict, List, Optional

# Base model types in the bundled list
EXPRESSION_MODEL_TYPES = ("pony", "illustrious", "sdxl", "sd15", "flux")

# Other spellings accepted for --ae-expression-loras
_ALIASES = {
    "illu": "illustrious",
    "noobai": "illustrious",
    "noob": "illustrious",
    "xl": "sdxl",
    "sd1.5": "sd15",
    "sd1": "sd15",
    "sd-1.5": "sd15",
    "1.5": "sd15",
}


def normalize_expression_type(value: str) -> Optional[str]:
    """Map a model type or alias (e.g. 'NoobAI', 'sd1.5') to its key, or None if unknown"""
    key = value.strip().lower().replace("_", "")
    key = _ALIASES.get(key, key)
    return key if key in EXPRESSION_MODEL_TYPES else None


def load_expression_loras() -> List[Dict]:
    """
    Read the bundled expression LoRA list as a flat list

    Each entry keeps the AutoExpress fields and gains model_type (the base model
    it belongs to) and url (its civitai.red model version page).
    """
    data = resources.files("civitai_downloader").joinpath("resources/expression_loras.json").read_text(encoding="utf-8")
    loras = []
    for model_type, entries in json.loads(data).items():
        if model_type.startswith("_"):
            continue
        for entry in entries:
            url = (f"https://civitai.red/models/{entry['civitai_model_id']}"
                   f"?modelVersionId={entry['civitai_version_id']}")
            loras.append({**entry, "model_type": model_type, "url": url})
    return loras


def expression_loras_for(model_types: Optional[List[str]] = None) -> List[Dict]:
    """Expression LoRAs for the given model types, or all of them when none are given"""
    loras = load_expression_loras()
    if not model_types:
        return loras
    wanted = set(model_types)
    return [lora for lora in loras if lora["model_type"] in wanted]
