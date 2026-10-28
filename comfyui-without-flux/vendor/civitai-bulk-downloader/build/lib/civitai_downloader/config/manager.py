"""
Configuration management for CivitAI Model Downloader
"""

import json
from pathlib import Path
from typing import Dict, Optional

from .ui_presets import UI_PRESETS, CONFIG_LAYOUT_UIS, normalize_ui


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.cwd() / "config.json"
        self.config = self.load_config()
        self.ui: Optional[str] = None
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            self.create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "civitai_api_key": "",
            "csvs_directory": "CSVs",
            "model_paths": {
                "checkpoint": "models/Stable-diffusion",
                "lora": "models/Lora",
                "locon": "models/Lora",
                "lycoris": "models/Lora",
                "controlnet": "models/ControlNet",
                "hypernetwork": "models/hypernetworks",
                "vae": "models/VAE",
                "poses": "models/Poses",
                "textualinversion": "Embeddings",
                "upscaler": "models/ESRGAN",
                "aestheticgradient": "extensions/stable-diffusion-webui-aesthetic-gradients/aesthetic_embeddings",
                "motionmodule": "extensions/sd-webui-animatediff/model",
                "other": "models/Other"
            },
            "download_settings": {
                "max_concurrent_downloads": 4,
                "timeout": 30,
                "retry_attempts": 3
            }
        }
    
    def create_default_config(self):
        """Create default configuration file"""
        config = self.get_default_config()
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
    
    def get_api_key(self) -> str:
        """Get CivitAI API key"""
        return self.config.get("civitai_api_key", "")
    
    def set_api_key(self, api_key: str):
        """Set CivitAI API key"""
        self.config["civitai_api_key"] = api_key
        self.save_config()
    
    def get_model_paths(self) -> Dict[str, str]:
        """
        Get model paths for the active UI
        
        A1111, Forge and reForge use config.json's model_paths so custom folders
        still apply; other UIs use their own preset layout.
        """
        ui = self.get_ui()
        if ui and ui not in CONFIG_LAYOUT_UIS:
            return dict(UI_PRESETS[ui])
        return self.config.get("model_paths", {})
    
    def get_ui(self) -> Optional[str]:
        """Get the active UI (set for this run, else the 'ui' key in config.json)"""
        return self.ui or normalize_ui(self.config.get("ui"))
    
    def set_ui(self, ui: Optional[str]):
        """Set the UI whose folder layout is used for this run (not saved to config.json)"""
        self.ui = normalize_ui(ui)
    
    def get_csvs_directory(self) -> str:
        """Get CSVs directory path"""
        return self.config.get("csvs_directory", "CSVs")
    
    def get_download_settings(self) -> Dict:
        """Get download settings"""
        return self.config.get("download_settings", {})
    
    def update_config(self, updates: Dict):
        """Update configuration with new values"""
        self.config.update(updates)
        self.save_config()
    
    def set_csvs_directory(self, path: str):
        """Set CSVs directory path"""
        self.config["csvs_directory"] = path
        self.save_config()
