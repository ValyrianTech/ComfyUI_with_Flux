"""
CivitAI API client for querying models and getting download links
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
from loguru import logger

from ..config.urls import CIVITAI_API_BASE, api_base, download_url_for, hosts_to_try


class CivitAIApiClient:
    """Client for interacting with CivitAI API"""
    
    BASE_URL = f"{CIVITAI_API_BASE}/"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request to CivitAI, trying the other hosts when one doesn't have it"""
        if not self.session:
            raise RuntimeError("API client not initialized. Use async context manager.")
        
        for host in hosts_to_try():
            url = urljoin(f"{api_base(host)}/", endpoint)
            logger.debug(f"Making API request to: {url} with params: {params}")
            
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Successful API response from {endpoint} on {host}")
                        return data
                    elif response.status == 404:
                        logger.debug(f"{endpoint} not found on {host}")
                        continue
                    else:
                        logger.error(f"API request failed: {response.status} for {endpoint}")
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )
            except Exception as e:
                logger.error(f"API request error for {endpoint}: {e}")
                raise
        
        logger.warning(f"API endpoint not found on any CivitAI host: {endpoint}")
        return {}
    
    async def search_models_by_name(self, name: str, model_type: Optional[str] = None) -> List[Dict]:
        """Search for models by name"""
        params = {
            "query": name,
            "limit": 10
        }
        
        if model_type:
            # Map internal types to API types
            type_mapping = {
                "checkpoint": "Checkpoint",
                "lora": "LORA",
                "locon": "LORA",
                "lycoris": "LORA",
                "controlnet": "Controlnet",
                "hypernetwork": "Hypernetwork",
                "textualinversion": "TextualInversion",
                "poses": "Poses",
                "aestheticgradient": "AestheticGradient"
            }
            api_type = type_mapping.get(model_type.lower())
            if api_type:
                params["types"] = api_type
        
        response = await self._make_request("models", params)
        return response.get("items", [])
    
    async def get_model_by_id(self, model_id: int) -> Optional[Dict]:
        """Get model details by ID"""
        response = await self._make_request(f"models/{model_id}")
        return response if response else None
    
    async def get_model_version(self, version_id: int) -> Optional[Dict]:
        """Get model version details by version ID"""
        response = await self._make_request(f"model-versions/{version_id}")
        return response if response else None
    
    def extract_download_url(self, model_data: Dict, prefer_safetensor: bool = True) -> Optional[str]:
        """Extract download URL from model data"""
        if not model_data:
            return None
        
        # Get the latest model version
        model_versions = model_data.get("modelVersions", [])
        if not model_versions:
            return None
        
        latest_version = model_versions[0]  # First version is usually the latest
        
        # Check if downloadUrl is directly available
        if "downloadUrl" in latest_version:
            return latest_version["downloadUrl"]
        
        # Look through files for the best match
        files = latest_version.get("files", [])
        if not files:
            return None
        
        # Prefer SafeTensor format
        safetensor_file = None
        primary_file = None
        any_file = None
        
        for file in files:
            file_format = file.get("metadata", {}).get("format", "").lower()
            is_primary = file.get("primary", False)
            
            if file_format == "safetensor":
                safetensor_file = file
                if is_primary:
                    break
            elif is_primary:
                primary_file = file
            
            if not any_file:
                any_file = file
        
        # Choose the best file
        chosen_file = safetensor_file or primary_file or any_file
        
        if chosen_file:
            # Construct download URL
            version_id = latest_version.get("id")
            if version_id:
                return download_url_for(version_id)
        
        return None
    
    async def find_download_url(self, model_name: str, model_id: Optional[str] = None, 
                               model_type: Optional[str] = None) -> Optional[str]:
        """
        Find download URL for a model by name or ID
        
        Args:
            model_name: Name of the model to search for
            model_id: Optional model ID if available
            model_type: Optional model type to filter search
            
        Returns:
            Download URL if found, None otherwise
        """
        try:
            # If we have a model ID, try that first
            if model_id and model_id.isdigit():
                model_data = await self.get_model_by_id(int(model_id))
                if model_data:
                    download_url = self.extract_download_url(model_data)
                    if download_url:
                        return download_url
            
            # Search by name
            search_results = await self.search_models_by_name(model_name, model_type)
            
            # Look for exact name match first
            for model in search_results:
                if model.get("name", "").lower() == model_name.lower():
                    download_url = self.extract_download_url(model)
                    if download_url:
                        return download_url
            
            # If no exact match, try first result
            if search_results:
                first_result = search_results[0]
                download_url = self.extract_download_url(first_result)
                if download_url:
                    return download_url
        
        except Exception as e:
            print(f"Error finding download URL for {model_name}: {e}")
        
        return None
