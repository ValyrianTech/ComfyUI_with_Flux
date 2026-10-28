"""
CSV processing and model management utilities
"""

import csv
from pathlib import Path
from typing import List, Tuple, Dict, Optional


class CSVProcessor:
    """Handles CSV file processing for model data"""
    
    @staticmethod
    def read_model_csv(csv_path: Path) -> List[Tuple[str, str, str, str]]:
        """
        Read model data from CSV file
        
        Returns:
            List of tuples (index, model_id, model_name, url)
        """
        if not csv_path.exists() or csv_path.stat().st_size == 0:
            return []
        
        models = []
        try:
            with open(csv_path, "r", encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                
                for row in csv_reader:
                    # Skip header row or empty rows
                    if len(row) < 4 or row[0].lower() in ['srno', 'sr no', 'index']:
                        continue
                    
                    try:
                        index, model_id, model_name, url = row[:4]
                        if model_name.strip() and (url.strip() or model_id.strip()):
                            models.append((
                                index.strip(),
                                model_id.strip(),
                                model_name.strip(),
                                url.strip()
                            ))
                    except ValueError:
                        continue
        
        except Exception as e:
            print(f"Error reading CSV file {csv_path}: {e}")
        
        return models
    
    @staticmethod
    def get_model_types(csvs_directory: Path) -> List[str]:
        """Get list of available model types from CSV files"""
        if not csvs_directory.exists():
            return []
        
        files = csvs_directory.glob("*.csv")
        model_types = [path.stem for path in files if path.is_file()]
        
        # Remove template from the list
        if "template" in model_types:
            model_types.remove("template")
        
        return model_types


class ModelManager:
    """Manages model download operations"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.csv_processor = CSVProcessor()
    
    # CivitAI API model types that map to a different config key than their lowercase name
    API_TYPE_ALIASES = {
        "dora": "lora",
    }
    
    def model_type_key(self, api_type: Optional[str]) -> str:
        """Map a CivitAI API model type (e.g. 'LORA', 'TextualInversion') to a model_paths key"""
        if not api_type:
            return "other"
        
        key = api_type.replace(" ", "").lower()
        key = self.API_TYPE_ALIASES.get(key, key)
        
        if key in self.config_manager.get_model_paths():
            return key
        return "other"
    
    def get_download_path(self, model_type: str, main_path: Path) -> Path:
        """Get the download path for a specific model type"""
        model_paths = self.config_manager.get_model_paths()
        
        try:
            sub_dir = Path(model_paths[model_type])
        except KeyError:
            sub_dir = Path(model_paths.get("other", "models/Other"))
        
        download_path = Path(main_path, sub_dir)
        download_path.mkdir(parents=True, exist_ok=True)
        
        return download_path
    
    def prepare_download_tasks(self, model_type: str, main_path: Path, 
                              missing_urls_handler=None) -> List[Tuple[str, Path]]:
        """
        Prepare download tasks for a model type
        
        Args:
            model_type: Type of model (checkpoint, lora, etc.)
            main_path: Base path for downloads
            missing_urls_handler: Optional async function to handle missing URLs
            
        Returns:
            List of (url, file_path) tuples ready for download
        """
        # Get CSV path
        csvs_dir = self.config_manager.get_csvs_directory()
        root_dir = Path.cwd()
        csv_path = root_dir / csvs_dir / f"{model_type}.csv"
        
        # Read models from CSV
        models = self.csv_processor.read_model_csv(csv_path)
        
        if not models:
            print(f"No valid models found in {csv_path}")
            return []
        
        # Get download path
        download_path = self.get_download_path(model_type, main_path)
        
        # Prepare download tasks
        download_tasks = []
        missing_url_tasks = []
        
        for index, model_id, model_name, url in models:
            file_path = download_path / f"{model_name}.safetensors"
            
            if url:
                # URL is available, add to download tasks
                download_tasks.append((url, file_path))
            else:
                # URL is missing, add to tasks that need URL resolution
                missing_url_tasks.append((model_id, model_name, file_path))
        
        # If we have missing URLs and a handler, process them
        if missing_url_tasks and missing_urls_handler:
            print(f"Found {len(missing_url_tasks)} models without URLs, attempting to resolve...")
            resolved_tasks = missing_urls_handler(missing_url_tasks, model_type)
            if resolved_tasks:
                download_tasks.extend(resolved_tasks)
        
        return download_tasks
    
    def get_available_model_types(self) -> List[str]:
        """Get list of available model types from CSV files"""
        csvs_dir = self.config_manager.get_csvs_directory()
        root_dir = Path.cwd()
        csvs_directory = root_dir / csvs_dir
        
        return self.csv_processor.get_model_types(csvs_directory)
