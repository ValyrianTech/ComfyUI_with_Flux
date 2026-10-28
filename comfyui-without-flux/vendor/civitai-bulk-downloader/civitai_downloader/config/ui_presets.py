"""
Model folder layouts for the different Stable Diffusion UIs
"""

from pathlib import Path
from typing import Dict, Optional

# AUTOMATIC1111 layout, shared by Forge and reForge
_A1111_PATHS = {
    "checkpoint": "models/Stable-diffusion",
    "lora": "models/Lora",
    "locon": "models/Lora",
    "lycoris": "models/Lora",
    "controlnet": "models/ControlNet",
    "hypernetwork": "models/hypernetworks",
    "vae": "models/VAE",
    "poses": "models/Poses",
    "textualinversion": "embeddings",
    "upscaler": "models/ESRGAN",
    "aestheticgradient": "extensions/stable-diffusion-webui-aesthetic-gradients/aesthetic_embeddings",
    "motionmodule": "extensions/sd-webui-animatediff/model",
    "other": "models/Other",
}

UI_PRESETS: Dict[str, Dict[str, str]] = {
    "a1111": _A1111_PATHS,
    "forge": _A1111_PATHS,
    "reforge": _A1111_PATHS,
    "sdnext": {
        "checkpoint": "models/Stable-diffusion",
        "lora": "models/Lora",
        "locon": "models/Lora",
        "lycoris": "models/Lora",
        "controlnet": "models/control/controlnet",
        "hypernetwork": "models/hypernetworks",
        "vae": "models/VAE",
        "poses": "models/Poses",
        "textualinversion": "models/embeddings",
        "upscaler": "models/ESRGAN",
        "other": "models/Other",
    },
    "comfyui": {
        "checkpoint": "models/checkpoints",
        "lora": "models/loras",
        "locon": "models/loras",
        "lycoris": "models/loras",
        "controlnet": "models/controlnet",
        "hypernetwork": "models/hypernetworks",
        "vae": "models/vae",
        "poses": "models/poses",
        "textualinversion": "models/embeddings",
        "upscaler": "models/upscale_models",
        "motionmodule": "models/animatediff_models",
        "other": "models/other",
    },
    "fooocus": {
        "checkpoint": "models/checkpoints",
        "lora": "models/loras",
        "locon": "models/loras",
        "lycoris": "models/loras",
        "controlnet": "models/controlnet",
        "vae": "models/vae",
        "textualinversion": "models/embeddings",
        "upscaler": "models/upscale_models",
        "other": "models/other",
    },
    "swarmui": {
        "checkpoint": "Models/Stable-Diffusion",
        "lora": "Models/Lora",
        "locon": "Models/Lora",
        "lycoris": "Models/Lora",
        "controlnet": "Models/controlnet",
        "vae": "Models/VAE",
        "textualinversion": "Models/Embeddings",
        "upscaler": "Models/upscale_models",
        "other": "Models/other",
    },
}

UI_ALIASES = {
    "automatic1111": "a1111",
    "webui": "a1111",
    "sd-webui": "a1111",
    "sd-forge": "forge",
    "sd-reforge": "reforge",
    "next": "sdnext",
    "sd.next": "sdnext",
    "sd-next": "sdnext",
    "vladmandic": "sdnext",
    "comfy": "comfyui",
    "swarm": "swarmui",
}

# UIs whose layout follows config.json's model_paths, so user customisations still apply
CONFIG_LAYOUT_UIS = {"a1111", "forge", "reforge"}


def normalize_ui(name: Optional[str]) -> Optional[str]:
    """Map a user-supplied UI name to a preset key, or None if unknown"""
    if not name:
        return None
    key = name.strip().lower().replace("_", "-")
    key = UI_ALIASES.get(key, key)
    return key if key in UI_PRESETS else None


def detect_ui(root: Path) -> Optional[str]:
    """Guess which UI is installed at root from files each one ships with"""
    root = Path(root)

    def has(*names: str) -> bool:
        return all((root / name).exists() for name in names)

    if has("comfy") and has("custom_nodes"):
        return "comfyui"
    if has("fooocus_version.py"):
        return "fooocus"
    if has("launchtools") or (has("Models") and has("src/bin")):
        return "swarmui"
    if has("installer.py", "modules"):
        return "sdnext"
    if has("modules_forge"):
        # reForge is a fork of Forge and keeps the same folder layout
        return "forge"
    if has("webui.py") or has("launch.py", "modules"):
        return "a1111"
    return None
