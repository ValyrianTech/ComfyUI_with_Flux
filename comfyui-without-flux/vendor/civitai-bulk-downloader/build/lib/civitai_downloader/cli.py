#!/usr/bin/env python3
"""
CivitAI Model Downloader - CLI Interface
"""

import asyncio
import os
import subprocess
import sys
import argparse
from pathlib import Path
from typing import Optional

import aiohttp
from loguru import logger

from .config.ui_presets import detect_ui, normalize_ui
from .expression_loras import EXPRESSION_MODEL_TYPES, expression_loras_for, normalize_expression_type
from . import ConfigManager, CivitAIApiClient, FileDownloader, ModelManager, URLPreprocessor, preprocess_urls, process_single_url

# UI names accepted by --ui (see civitai_downloader/config/ui_presets.py for the folder layouts)
UI_CHOICES = ("a1111", "forge", "reforge", "sdnext", "comfyui", "fooocus", "swarmui")

def ui_name(value: str) -> str:
    """argparse type for --ui: accepts preset names and common aliases (e.g. 'next', 'comfy')"""
    ui = normalize_ui(value)
    if not ui:
        raise argparse.ArgumentTypeError(
            f"unknown UI '{value}' (choose from {', '.join(UI_CHOICES)})"
        )
    return ui


def expression_type(value: str) -> str:
    """argparse type for --ae-expression-loras: accepts base model types and aliases (e.g. 'noobai', 'sd1.5')"""
    model_type = normalize_expression_type(value)
    if not model_type:
        raise argparse.ArgumentTypeError(
            f"unknown model type '{value}' (choose from {', '.join(EXPRESSION_MODEL_TYPES)})"
        )
    return model_type


def format_size(num_bytes: int) -> str:
    """Human-readable file size, e.g. 6.46 GB"""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"


# Environment variables checked for the CivitAI API key when --api-key is not given
API_KEY_ENV_VARS = ("CAI_API_KEY", "CIVITAI_API_KEY")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="CivitAI Model Downloader - Download models for Stable Diffusion",
        epilog="""
Examples:
  %(prog)s --sd /path/to/stable-diffusion --csv ./my-csvs --api-key your-api-key
  %(prog)s --sd ~/stable-diffusion-webui
  %(prog)s --api-key your-civitai-api-key
  %(prog)s --preprocess --api-key your-api-key
  %(prog)s --preprocess --csv ./my-csvs --text-files
  %(prog)s --url "https://civitai.red/models/4201/realistic-vision" --sd ~/stable-diffusion-webui
  %(prog)s --api-key CAI_API_KEY --url "https://civitai.red/api/download/models/130072" --sd ~/stable-diffusion-webui
  %(prog)s --url "https://civitai.red/models/4201?modelVersionId=130072" --url 4201 --sd ~/stable-diffusion-webui
  %(prog)s --url "https://civitai.red/api/download/models/130072" --type lora --sd ~/stable-diffusion-webui
  %(prog)s --url "https://civitai.red/models/4201/realistic-vision" --output ~/Downloads/models
  %(prog)s --url URL1 URL2 URL3 --sd ~/stable-diffusion-webui
  %(prog)s --url URL1 URL2 --sd ~/ComfyUI --ui comfyui
  %(prog)s --url-file my-models.txt --output ~/Downloads/models
  %(prog)s --url "https://civitai.red/models/4201/realistic-vision" --resolve-only
  %(prog)s --sd ~/ComfyUI --ae-expression-loras
  %(prog)s --ae-expression-loras pony illustrious --sd ~/stable-diffusion-webui
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--sd", "--stable-diffusion",
        dest="sd_path",
        type=str,
        help="Path to the Stable Diffusion UI installation directory (A1111, Forge, ComfyUI, ...)"
    )
    
    parser.add_argument(
        "--ui",
        dest="ui",
        type=ui_name,
        metavar="UI",
        help=f"Which UI is installed at --sd ({', '.join(UI_CHOICES)}), so models go into "
             "that UI's folders. "
             "Detected from the install when omitted (falls back to config.json's model_paths)"
    )
    
    parser.add_argument(
        "--csv", "--csvs-dir",
        dest="csvs_dir",
        type=str,
        help="Path to CSV files directory (default: CSVs)"
    )
    
    parser.add_argument(
        "--api-key",
        dest="api_key",
        type=str,
        help="CivitAI API key, or the name of an environment variable holding it "
             "(e.g. CAI_API_KEY). Falls back to the CAI_API_KEY or CIVITAI_API_KEY "
             "environment variable, then config.json"
    )
    
    parser.add_argument(
        "--preprocess",
        action="store_true",
        help="Preprocess CSV files to convert non-download URLs to proper download URLs before downloading"
    )
    
    parser.add_argument(
        "--url", "--urls",
        dest="urls",
        nargs="+",
        action="extend",
        metavar="URL",
        help="Download models from CivitAI model page URLs, version URLs, download URLs, model IDs "
             "or names. Accepts several values and can be repeated. Each model is saved into "
             "its type folder (checkpoint, lora, ...) based on CivitAI's metadata"
    )
    
    parser.add_argument(
        "--url-file",
        dest="url_file",
        type=str,
        metavar="FILE",
        help="Text file with one URL/ID/name per line to download (blank lines and lines "
             "starting with # are ignored). Can be combined with --url"
    )
    
    parser.add_argument(
        "--ae-expression-loras", "--expression-loras",
        dest="expression_loras",
        nargs="*",
        type=expression_type,
        metavar="MODEL_TYPE",
        help="Download the AutoExpress expression LoRAs into the LoRA folder. Optionally limit "
             f"them to base model types ({', '.join(EXPRESSION_MODEL_TYPES)}); all are "
             "downloaded when none are given. Can be combined with --url"
    )
    
    parser.add_argument(
        "--type",
        dest="model_type",
        type=str,
        help="Force every --url download into this model type folder (e.g. checkpoint, lora) "
             "instead of detecting it from CivitAI"
    )
    
    parser.add_argument(
        "-o", "--output",
        dest="output_dir",
        type=str,
        help="Directory to save --url downloads into instead of a Stable Diffusion install. "
             "Models are sorted into a subfolder per type (e.g. OUTPUT/lora), or into the "
             "--ui layout when --ui is given"
    )
    
    parser.add_argument(
        "--flat",
        action="store_true",
        help="With --output, save every model directly in the output directory without type subfolders"
    )
    
    parser.add_argument(
        "--no-aria2",
        action="store_true",
        help="Use the built-in downloader even when aria2c is installed"
    )
    
    parser.add_argument(
        "--connections",
        type=int,
        metavar="N",
        help="Connections per file when downloading with aria2c (1-16, default 16)"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Check each file's SHA256 against CivitAI, both for new downloads and before "
             "skipping existing files (slower for large models)"
    )
    
    parser.add_argument(
        "--resolve-only",
        action="store_true",
        help="With --url, only display the resolved download URL and model info without downloading"
    )
    
    parser.add_argument(
        "--text-files",
        action="store_true",
        help="Include .txt files when preprocessing (creates CSV output)"
    )
    
    return parser.parse_args()


# Configure logging
def setup_logging():
    """Setup loguru logging to both file and stdout"""
    # Remove default handler
    logger.remove()
    
    # Add stdout handler with INFO level
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True
    )
    
    # Add file handler with DEBUG level
    logger.add(
        "downloads.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    logger.info("Logging initialized - writing to downloads.log")


class CivitAIDownloaderCLI:
    """Command Line Interface for CivitAI Model Downloader"""
    
    def __init__(self, args=None):
        self.args = args or argparse.Namespace()
        self.config_manager = ConfigManager()
        
        # Apply CLI overrides for configuration
        if hasattr(self.args, 'csvs_dir') and self.args.csvs_dir:
            # Update the CSV directory path in config
            logger.info(f"Using CSV directory from CLI: {self.args.csvs_dir}")
            self.config_manager.set_csvs_directory(self.args.csvs_dir)
        
        # Apply UI layout from CLI if provided
        if getattr(self.args, 'ui', None):
            logger.info(f"Using {self.args.ui} folder layout from CLI")
            self.config_manager.set_ui(self.args.ui)
        
        # Apply API key from CLI or environment if provided
        self.api_key_source = self.apply_api_key_override()
        
        self.model_manager = ModelManager(self.config_manager)
    
    def apply_api_key_override(self) -> Optional[str]:
        """
        Resolve the API key from the CLI or environment, in this order:
        
        1. --api-key VALUE, where VALUE may also be the name of an exported
           environment variable holding the key (e.g. --api-key CAI_API_KEY)
        2. The CAI_API_KEY (or CIVITAI_API_KEY) environment variable
        3. The key saved in config.json
        
        Keys read from the environment are used for this run only and are never
        written to config.json.
        """
        cli_value = getattr(self.args, 'api_key', None)
        if cli_value:
            env_value = os.environ.get(cli_value, "").strip()
            if env_value:
                logger.info(f"Using API key from environment variable {cli_value}")
                self.config_manager.config["civitai_api_key"] = env_value
                return "env"
            logger.info("Using API key from CLI")
            self.config_manager.set_api_key(cli_value)
            return "cli"
        
        for env_name in API_KEY_ENV_VARS:
            env_value = os.environ.get(env_name, "").strip()
            if env_value:
                logger.info(f"Using API key from environment variable {env_name}")
                self.config_manager.config["civitai_api_key"] = env_value
                return "env"
        
        return None
    
    def setup_api_key(self):
        """Setup CivitAI API key if not configured"""
        api_key = self.config_manager.get_api_key()
        
        # If API key was provided via CLI or environment, we're done
        if self.api_key_source:
            logger.info(f"API key configured via {self.api_key_source.upper()}")
            return
        
        if api_key:
            logger.info(f"Using API key from {self.config_manager.config_path} "
                        f"(set {API_KEY_ENV_VARS[0]} or pass --api-key to override)")
            return
        
        if not api_key:
            logger.info("CivitAI API Key Setup")
            print("\nCivitAI API Key Setup")
            print("To download models from CivitAI, you need an API key.")
            print("1. Go to https://civitai.red/user/account")
            print("2. Create an API token")
            print("3. Copy the token and paste it below")
            
            while True:
                try:
                    api_key = input("Enter your CivitAI API key (or press Enter to skip): ").strip()
                except EOFError:
                    # Non-interactive run (e.g. scripted CLI usage): continue without a key
                    logger.warning("No API key provided and no interactive input available")
                    print("\nWarning: Continuing without an API key.")
                    break
                if api_key:
                    self.config_manager.set_api_key(api_key)
                    logger.success("API key saved successfully!")
                    print("API key saved successfully!")
                    break
                else:
                    logger.warning("User chose to continue without API key")
                    print("Warning: Without an API key, you may not be able to download some models.")
                    confirm = input("Continue without API key? (y/n): ").lower()
                    if confirm == 'y':
                        break
    
    def apply_ui_layout(self, main_path: Path):
        """Detect the UI at main_path when none was chosen via --ui or config.json"""
        ui = self.args.ui if getattr(self.args, 'ui', None) else None
        ui = ui or self.config_manager.config.get("ui")
        if not ui:
            ui = detect_ui(main_path)
            if ui:
                logger.info(f"Detected {ui} install at {main_path}")
        self.config_manager.set_ui(ui)
        ui = self.config_manager.get_ui()
        
        if ui:
            print(f"Using {ui} folder layout")
        else:
            logger.info("No UI detected, using model_paths from config.json")
    
    def is_valid_ui_root(self, main_path: Path) -> bool:
        """Check that main_path contains the top-level models folder of the active layout"""
        checkpoint_dir = self.config_manager.get_model_paths().get("checkpoint", "models")
        return (main_path / Path(checkpoint_dir).parts[0]).is_dir()
    
    def get_stable_diffusion_path(self) -> Optional[Path]:
        """Get and validate Stable Diffusion installation path"""
        logger.info("Starting Stable Diffusion path validation")
        
        # Check if path was provided via CLI argument
        if hasattr(self.args, 'sd_path') and self.args.sd_path:
            logger.info(f"Using Stable Diffusion path from CLI: {self.args.sd_path}")
            main_path = Path(self.args.sd_path).expanduser()
            
            if not main_path.exists():
                logger.error(f"CLI provided path does not exist: {main_path}")
                print(f"Error: CLI provided path does not exist: {main_path}")
                return None
            
            # Check if models folder exists (simplified validation)
            self.apply_ui_layout(main_path)
            if self.is_valid_ui_root(main_path):
                logger.success(f"Valid Stable Diffusion path found: {main_path}")
                print(f"Using Stable Diffusion path: {main_path}")
                return main_path
            else:
                logger.error(f"Invalid CLI path - no models folder found: {main_path}")
                print(f"Error: Invalid CLI path. The Stable Diffusion directory must contain a 'models' folder.")
                return None
        
        # Interactive path selection if no CLI argument provided
        while True:
            path_input = input("\nEnter your Stable Diffusion installation path: ").strip()
            
            if not path_input:
                logger.warning("Empty path provided by user")
                print("Please enter a valid path.")
                continue
                
            main_path = Path(path_input)
            logger.debug(f"Checking path: {main_path}")
            
            if not main_path.exists():
                logger.warning(f"Path does not exist: {main_path}")
                print("Path does not exist. Please enter a valid path.")
                continue
            
            # Check if models folder exists (simplified validation)
            self.apply_ui_layout(main_path)
            if self.is_valid_ui_root(main_path):
                logger.success(f"Valid Stable Diffusion path found: {main_path}")
                print("Valid Stable Diffusion path found.")
                return main_path
            else:
                logger.warning(f"Invalid path - no models folder found: {main_path}")
                print("Invalid path. The Stable Diffusion directory must contain a 'models' folder.")
                retry = input("Try again? (y/n): ").lower()
                if retry != 'y':
                    logger.info("User chose to exit path validation")
                    return None
    
    async def preprocess_csv_files(self):
        """Preprocess CSV files to resolve URLs to download URLs"""
        logger.info("Starting CSV URL preprocessing...")
        print("\n🔄 Preprocessing CSV files...")
        print("Converting non-download URLs to proper download URLs using CivitAI API")
        
        api_key = self.config_manager.get_api_key()
        csvs_dir = Path(self.config_manager.get_csvs_directory())
        
        if not api_key:
            logger.warning("No API key available for preprocessing")
            print("⚠️  Warning: No API key configured. Some protected models may not be accessible.")
            print("Consider setting an API key for better results.")
        
        try:
            results = await preprocess_urls(api_key, csvs_dir, getattr(self.args, 'text_files', False))
            
            if not results:
                logger.info("No files found to preprocess")
                print("No files found to preprocess")
                return
            
            # Display results
            total_all = 0
            success_all = 0
            failed_all = 0
            
            print(f"\n📊 Preprocessing Results:")
            for filename, (total, success, failed) in results.items():
                print(f"  {filename}:")
                print(f"    Total processed: {total}")
                print(f"    Successfully resolved: {success}")
                if failed > 0:
                    print(f"    Failed to resolve: {failed}")
                
                total_all += total
                success_all += success
                failed_all += failed
            
            print(f"\n📈 Overall Summary:")
            print(f"  Total URLs processed: {total_all}")
            print(f"  Successfully resolved: {success_all}")
            print(f"  Failed to resolve: {failed_all}")
            
            if total_all > 0:
                success_rate = (success_all / total_all) * 100
                print(f"  Success rate: {success_rate:.1f}%")
                
            logger.info(f"Preprocessing completed: {success_all}/{total_all} URLs resolved")
            
        except Exception as e:
            logger.error(f"Error during preprocessing: {e}")
            print(f"❌ Error during preprocessing: {e}")
            raise
    
    async def process_single_url(self, url: str):
        """Process a single URL and display the result"""
        logger.info("Processing single URL...")
        print("\n🔗 Processing single URL...")
        
        api_key = self.config_manager.get_api_key()
        
        print(f"Input: {url}")
        
        try:
            success, result, metadata = await process_single_url(url, api_key)
            
            if success:
                print(f"\n✅ Successfully resolved!")
                print(f"📥 Download URL: {result}")
                
                if metadata:
                    print(f"\n📋 Model Information:")
                    for key, value in metadata.items():
                        if key != 'download_url':  # Already shown above
                            print(f"   {key.replace('_', ' ').title()}: {value}")
                
                logger.success(f"Successfully processed URL: {url}")
            else:
                print(f"\n❌ Failed to resolve: {result}")
                logger.error(f"Failed to process URL: {url} - {result}")
                
        except Exception as e:
            logger.error(f"Error processing single URL: {e}")
            print(f"❌ Error processing URL: {e}")
            raise
    
    def get_download_settings(self) -> dict:
        """Download settings from config.json with CLI overrides applied"""
        download_settings = dict(self.config_manager.get_download_settings())
        if getattr(self.args, 'verify', False):
            download_settings["verify_hash"] = True
        if getattr(self.args, 'no_aria2', False):
            download_settings["use_aria2"] = False
        if getattr(self.args, 'connections', None):
            download_settings["aria2_connections"] = self.args.connections
        return download_settings
    
    def check_already_present(self, download_tasks: list) -> tuple:
        """
        Find models that are already fully downloaded before starting any downloads
        
        A file counts as present when it exists with exactly the size CivitAI
        reports. Files whose size isn't known up front are left in the queue and
        checked against the server's size when their download starts.
        
        Returns:
            Tuple of (tasks still to download, number already present)
        """
        if not self.config_manager.get_download_settings().get("skip_existing_files", True):
            return download_tasks, 0
        
        print("\n🔎 Checking for models that are already present...")
        to_download = []
        present = 0
        for url, file_path, expected in download_tasks:
            expected_size = (expected or {}).get('size')
            part_path = file_path.with_name(file_path.name + ".part")
            
            if expected_size is None:
                to_download.append((url, file_path, expected))
                continue
            
            aria2_control = file_path.with_name(file_path.name + ".aria2")
            if file_path.exists() and aria2_control.exists():
                print(f"  ↻ {file_path.name}: partial download found, will resume")
            elif file_path.exists():
                actual_size = file_path.stat().st_size
                if actual_size == expected_size:
                    if getattr(self.args, 'verify', False):
                        # Hash is checked by the downloader, which skips the file if it matches
                        to_download.append((url, file_path, expected))
                        print(f"  ✓ {file_path.name}: present ({format_size(actual_size)}), will verify hash")
                    else:
                        present += 1
                        print(f"  ✓ {file_path.name}: already present ({format_size(actual_size)})")
                    continue
                print(f"  ↻ {file_path.name}: incomplete ({format_size(actual_size)} of "
                      f"{format_size(expected_size)}), will re-download")
            elif part_path.exists():
                print(f"  ↻ {file_path.name}: partial download found ({format_size(part_path.stat().st_size)} of "
                      f"{format_size(expected_size)}), will resume")
            else:
                print(f"  ↓ {file_path.name}: not present ({format_size(expected_size)})")
            to_download.append((url, file_path, expected))
        
        logger.info(f"{present} model(s) already present, {len(to_download)} to download")
        return to_download, present
    
    def collect_urls(self) -> list:
        """Gather URLs from --url and --url-file, dropping duplicates while keeping order"""
        urls = list(getattr(self.args, 'urls', None) or [])
        
        url_file = getattr(self.args, 'url_file', None)
        if url_file:
            url_file_path = Path(url_file).expanduser()
            try:
                with open(url_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            urls.append(line)
            except OSError as e:
                logger.error(f"Could not read URL file {url_file_path}: {e}")
                print(f"Error: Could not read URL file {url_file_path}: {e}")
                sys.exit(1)
        
        unique_urls = []
        for url in (u.strip() for u in urls):
            if url and url not in unique_urls:
                unique_urls.append(url)
        return unique_urls
    
    def collect_expression_loras(self) -> list:
        """Expression LoRAs selected with --ae-expression-loras (empty when the flag is absent)"""
        model_types = getattr(self.args, 'expression_loras', None)
        if model_types is None:
            return []
        loras = expression_loras_for(model_types)
        types_label = ', '.join(dict.fromkeys(model_types)) if model_types else 'all model types'
        print(f"\n🎭 AutoExpress expression LoRAs ({types_label}):")
        for lora in loras:
            trigger = f"trigger '{lora['trigger']}'" if lora.get('trigger') else "no trigger"
            print(f"  • [{lora['model_type']}] {lora['title']} ({trigger}, weight {lora['weight']})")
        return loras
    
    async def download_urls(self, urls: list, main_path: Optional[Path] = None,
                            output_dir: Optional[Path] = None,
                            forced_types: Optional[dict] = None) -> tuple:
        """
        Resolve URLs and download each model
        
        Each model is sorted into its type folder: under output_dir when given
        (or directly into it with --flat), otherwise the configured folder
        under the Stable Diffusion path. forced_types maps a URL to the model
        type folder it must go into regardless of --type or CivitAI's metadata.
        """
        logger.info(f"Downloading {len(urls)} model(s) from URL")
        print(f"\n🔗 Resolving {len(urls)} URL(s)...")
        
        api_key = self.config_manager.get_api_key()
        model_type_override = getattr(self.args, 'model_type', None)
        flat = getattr(self.args, 'flat', False)
        preprocessor = URLPreprocessor(api_key)
        
        download_tasks = []
        failed = 0
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                success, target = await preprocessor.resolve_download_target(session, url)
                if not success:
                    print(f"  ✗ {url}: {target}")
                    failed += 1
                    continue
                
                if forced_types and url in forced_types:
                    model_type = forced_types[url]
                elif model_type_override:
                    model_type = model_type_override.lower()
                else:
                    model_type = self.model_manager.model_type_key(target['model_type'])
                if output_dir and getattr(self.args, 'ui', None) and not flat:
                    # Lay the output directory out like the chosen UI
                    download_path = self.model_manager.get_download_path(model_type, output_dir)
                elif output_dir:
                    download_path = output_dir if flat else output_dir / model_type
                    download_path.mkdir(parents=True, exist_ok=True)
                else:
                    download_path = self.model_manager.get_download_path(model_type, main_path)
                
                file_name = target['file_name']
                if not file_name:
                    base_name = target['model_name'] or f"model_{target['model_version_id'] or len(download_tasks) + 1}"
                    file_name = f"{base_name}.safetensors"
                file_path = download_path / Path(file_name).name
                
                label = target['model_name'] or url
                if target['version_name']:
                    label = f"{label} ({target['version_name']})"
                
                # Different inputs (e.g. a model page and its download link) can point to the same file
                if any(task[1] == file_path for task in download_tasks):
                    print(f"  = {label} already queued ({url})")
                    continue
                
                print(f"  ✓ {label} → {file_path}")
                expected = {'size': target.get('file_size'), 'sha256': target.get('file_sha256')}
                download_tasks.append((target['download_url'], file_path, expected))
        
        download_tasks, already_present = self.check_already_present(download_tasks)
        
        if not download_tasks:
            if already_present:
                print(f"\nNothing to download: all {already_present} model(s) are already present.")
            return 0, failed
        
        download_settings = self.get_download_settings()
        async with FileDownloader(api_key, download_settings) as downloader:
            results = await downloader.download_files(download_tasks, "URL Downloads")
        
        downloaded = sum(1 for success, message in results if success and "Skipped" not in message)
        skipped = sum(1 for success, message in results if success and "Skipped" in message)
        failed += sum(1 for success, _ in results if not success)
        
        print(f"\nURL Download Summary:")
        print(f"  Downloaded: {downloaded}")
        print(f"  Skipped (already exist): {skipped + already_present}")
        print(f"  Failed: {failed}")
        for success, message in results:
            if not success:
                logger.error(f"Failed download: {message}")
                print(f"  - {message}")
        
        logger.info(f"URL downloads completed: {downloaded} downloaded, {skipped} skipped, {failed} failed")
        return downloaded, failed
    
    async def resolve_missing_urls(self, missing_url_tasks, model_type):
        """Resolve missing URLs using CivitAI API"""
        api_key = self.config_manager.get_api_key()
        resolved_tasks = []
        
        if not api_key:
            logger.warning("API key required to resolve missing URLs")
            print("API key required to resolve missing URLs")
            return resolved_tasks
        
        logger.info(f"Resolving {len(missing_url_tasks)} missing URLs for {model_type}")
        async with CivitAIApiClient(api_key) as api_client:
            for model_id, model_name, file_path in missing_url_tasks:
                try:
                    logger.debug(f"Searching for model: {model_name} (ID: {model_id})")
                    print(f"  Searching for: {model_name}")
                    download_url = await api_client.find_download_url(
                        model_name, model_id, model_type
                    )
                    
                    if download_url:
                        resolved_tasks.append((download_url, file_path))
                        logger.success(f"Found download URL for {model_name}")
                        print(f"    ✓ Found download URL")
                    else:
                        logger.warning(f"Could not find download URL for {model_name}")
                        print(f"    ✗ Could not find download URL")
                
                except Exception as e:
                    logger.error(f"Error resolving URL for {model_name}: {e}")
                    print(f"    ✗ Error: {e}")
        
        logger.info(f"Resolved {len(resolved_tasks)} out of {len(missing_url_tasks)} URLs")
        return resolved_tasks
    
    async def download_model_type(self, model_type: str, main_path: Path) -> tuple:
        """Download models of a specific type"""
        logger.info(f"Processing {model_type.capitalize()} files...")
        print(f"\nProcessing {model_type.capitalize()} files...")
        
        # Prepare download tasks (with URL resolution for missing URLs)
        download_tasks = self.model_manager.prepare_download_tasks(
            model_type, 
            main_path, 
            self.resolve_missing_urls
        )
        
        if not download_tasks:
            logger.info(f"No files to download for {model_type}")
            print(f"No files to download for {model_type}")
            return 0, 0
        
        logger.info(f"Prepared {len(download_tasks)} download tasks for {model_type}")
        
        # Download files with progress tracking
        api_key = self.config_manager.get_api_key()
        download_settings = self.get_download_settings()
        max_concurrent = download_settings.get("max_concurrent_downloads", 4)
        
        print(f"📊 Downloading {len(download_tasks)} {model_type} files (max {max_concurrent} concurrent)")
        
        async with FileDownloader(api_key, download_settings) as downloader:
            results = await downloader.download_files(
                download_tasks, 
                f"{model_type.title()} Models"
            )
        
        # Count results with better categorization
        downloaded = sum(1 for success, message in results if success and "Skipped" not in message)
        skipped = sum(1 for success, message in results if success and "Skipped" in message)
        failed = sum(1 for success, _ in results if not success)
        
        logger.info(f"{model_type} download completed: {downloaded} downloaded, {skipped} skipped, {failed} failed")
        print(f"{model_type.capitalize()} Summary:")
        print(f"  Downloaded: {downloaded}")
        print(f"  Skipped (already exist): {skipped}")
        print(f"  Failed: {failed}")
        
        # Show failed downloads
        if failed > 0:
            logger.warning(f"Failed downloads for {model_type}:")
            print("Failed downloads:")
            for success, message in results:
                if not success:
                    logger.error(f"Failed download: {message}")
                    print(f"  - {message}")
        
        return downloaded, failed
    
    async def run(self):
        """Main CLI execution"""
        logger.info("Starting CivitAI Model Downloader")
        print("CivitAI Model Downloader")
        print("=" * 40)
        
        # Setup API key
        self.setup_api_key()
        
        # Handle URL downloads
        urls = self.collect_urls()
        forced_types = {}
        for lora in self.collect_expression_loras():
            forced_types[lora['url']] = "lora"
            if lora['url'] not in urls:
                urls.append(lora['url'])
        if urls:
            if getattr(self.args, 'resolve_only', False):
                for url in urls:
                    await self.process_single_url(url)
                return
            
            output_dir = getattr(self.args, 'output_dir', None)
            if output_dir:
                output_dir = Path(output_dir).expanduser()
                if output_dir.exists() and not output_dir.is_dir():
                    logger.error(f"Output path is not a directory: {output_dir}")
                    print(f"Error: Output path is not a directory: {output_dir}")
                    sys.exit(1)
                logger.info(f"Saving URL downloads to: {output_dir}")
                main_path = None
            else:
                main_path = self.get_stable_diffusion_path()
                if not main_path:
                    logger.error("Failed to get valid Stable Diffusion path")
                    print("Please rerun the script with a valid --sd or --output path.")
                    return
            
            _, failed = await self.download_urls(urls, main_path, output_dir, forced_types)
            if failed:
                sys.exit(1)
            return
        
        # Handle preprocessing if requested
        if hasattr(self.args, 'preprocess') and self.args.preprocess:
            await self.preprocess_csv_files()
            print("\n✅ Preprocessing completed! You can now run the downloader normally.")
            input("Press Enter to continue with downloads or Ctrl+C to exit...")
        
        # Get available model types
        models = self.model_manager.get_available_model_types()
        logger.info(f"Found model types: {models}")
        
        if not models:
            csvs_dir = self.config_manager.get_csvs_directory()
            logger.error(f"No model CSV files found in {csvs_dir} directory!")
            print(f"No model CSV files found in {csvs_dir} directory!")
            input("Press Enter to exit...")
            return
        
        # Get Stable Diffusion path
        main_path = self.get_stable_diffusion_path()
        if not main_path:
            logger.error("Failed to get valid Stable Diffusion path")
            input("Please rerun the script.\nPress Return to exit.")
            return
        
        logger.info(f"Using Stable Diffusion path: {main_path}")
        
        # Download models
        total_downloaded = 0
        total_failed = 0
        
        logger.info(f"Starting downloads for {len(models)} model types")
        for model_type in models:
            try:
                downloaded, failed = await self.download_model_type(model_type, main_path)
                total_downloaded += downloaded
                total_failed += failed
                
            except Exception as e:
                logger.error(f"Error downloading {model_type}: {e}")
                print(f"Error downloading {model_type}: {e}")
                total_failed += 1
        
        # Final summary
        logger.info(f"Download session completed: {total_downloaded} downloaded, {total_failed} failed")
        print(f"\nDownload Summary")
        print(f"Total Downloaded: {total_downloaded}")
        print(f"Total Failed: {total_failed}")
        
        if self.config_manager.get_download_settings().get("skip_existing_files", True):
            print("Note: Files that already existed were automatically skipped")
        
        input("\nPress Enter to exit...")


async def main(args=None):
    """Main entry point"""
    cli = CivitAIDownloaderCLI(args or parse_arguments())
    await cli.run()


def run():
    """Console script entry point for the civitai-download command"""
    args = parse_arguments()
    setup_logging()
    asyncio.run(main(args))


if __name__ == "__main__":
    run()
