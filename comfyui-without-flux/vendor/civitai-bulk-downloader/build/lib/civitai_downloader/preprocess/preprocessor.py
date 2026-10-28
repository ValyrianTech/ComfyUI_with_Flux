"""
Preprocessing module for CivitAI Model Downloader
Converts non-download URLs to proper download URLs using CivitAI API
"""

import re
import csv
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any
from urllib.parse import urlparse, parse_qs, parse_qsl, urlencode
from loguru import logger

from ..config.urls import CIVITAI_API_BASE, CIVITAI_HOST_PATTERN, api_base, download_url_for, host_of, hosts_to_try, to_civitai_host


class URLPreprocessor:
    """Preprocesses URLs in CSV files to ensure they are valid download URLs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = CIVITAI_API_BASE
        
        # URL patterns for different CivitAI URL types
        self.url_patterns = {
            'download_url': re.compile(CIVITAI_HOST_PATTERN + r'/api/download/models/(\d+)'),
            'model_page': re.compile(CIVITAI_HOST_PATTERN + r'/models/(\d+)'),
            'model_version_page': re.compile(CIVITAI_HOST_PATTERN + r'/models/(\d+)(?:/[^?#]*)?\?(?:.*&)?modelVersionId=(\d+)'),
            'model_id_only': re.compile(r'^(\d+)$'),
            'short_url': re.compile(CIVITAI_HOST_PATTERN + r'/models/(\d+)/?$'),
        }
    
    # Key added to API responses naming the CivitAI host that served them
    HOST_KEY = '_civitai_host'
    
    # Query parameters CivitAI expects to be numeric IDs
    NUMERIC_QUERY_PARAMS = ('fileId', 'modelVersionId', 'modelId')
    
    def sanitize_url(self, url: str) -> str:
        """
        Repair numeric ID query parameters on CivitAI links
        
        A link pasted without a separator can pick up trailing text, e.g.
        "...?fileId=2721540python". Keep the leading digits of such values and
        drop parameters that have none, so the link still downloads.
        """
        url = url.strip()
        if not self.url_patterns['download_url'].match(url) and not self.url_patterns['model_page'].match(url):
            return url
        
        parsed = urlparse(url)
        if not parsed.query:
            return url
        
        changed = False
        params = []
        for key, value in parse_qsl(parsed.query, keep_blank_values=True):
            if key in self.NUMERIC_QUERY_PARAMS and not value.isdigit():
                digits = re.match(r'\d+', value)
                changed = True
                if digits:
                    logger.warning(f"Ignoring trailing text '{value[digits.end():]}' after {key}={digits.group()} in {url}")
                    value = digits.group()
                else:
                    logger.warning(f"Dropping invalid {key}='{value}' from {url}")
                    continue
            params.append((key, value))
        
        if not changed:
            return url
        return parsed._replace(query=urlencode(params)).geturl()
    
    def identify_url_type(self, url: str) -> Tuple[str, Dict[str, str]]:
        """
        Identify the type of URL and extract relevant IDs
        
        Supports civitai.com, civitai.red and civitai.green over http/https, with or without
        "www.", including model pages with or without a name slug and with an
        optional modelVersionId query parameter.
        
        Returns:
            Tuple of (url_type, extracted_data)
        """
        url = url.strip()
        
        # Check for download URL (already correct format)
        match = self.url_patterns['download_url'].match(url)
        if match:
            return 'download_url', {'model_version_id': match.group(1)}
        
        # Check for model version page with modelVersionId parameter
        match = self.url_patterns['model_version_page'].match(url)
        if match:
            return 'model_version_page', {
                'model_id': match.group(1),
                'model_version_id': match.group(2)
            }
        
        # Check for general model page
        match = self.url_patterns['model_page'].match(url)
        if match:
            return 'model_page', {'model_id': match.group(1)}
        
        # Check for just a model ID
        match = self.url_patterns['model_id_only'].match(url)
        if match:
            return 'model_id_only', {'model_id': match.group(1)}
        
        # Try to extract from query parameters
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            if 'modelVersionId' in query_params:
                return 'query_version_id', {'model_version_id': query_params['modelVersionId'][0]}
            elif 'modelId' in query_params:
                return 'query_model_id', {'model_id': query_params['modelId'][0]}
        except Exception:
            pass
        
        return 'unknown', {'original_url': url}
    
    async def _get_json(self, session: aiohttp.ClientSession, path: str, what: str,
                        hosts: List[str], params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        GET an API path from the first CivitAI host that has it

        Hosts are tried in order and the next one is used whenever a host
        doesn't answer with 200, so a model missing on one site is still found
        on another. Returns None when no host has it.
        """
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        for host in hosts:
            url = f"{api_base(host)}/{path}"
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Retrieved {what} from {host}")
                        if isinstance(data, dict):
                            # The API's own downloadUrl isn't always on the host that answered
                            data[self.HOST_KEY] = host
                            for item in data.get('items') or []:
                                item[self.HOST_KEY] = host
                        return data
                    logger.warning(f"Failed to get {what} from {host}: {response.status}")
            except Exception as e:
                logger.error(f"Error getting {what} from {host}: {e}")
        return None
    
    async def get_model_info(self, session: aiohttp.ClientSession, model_id: str,
                             hosts: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get model information from CivitAI API"""
        return await self._get_json(session, f"models/{model_id}", f"model info for ID {model_id}",
                                    hosts or hosts_to_try())
    
    async def get_model_version_info(self, session: aiohttp.ClientSession, version_id: str,
                                     hosts: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get model version information from CivitAI API"""
        return await self._get_json(session, f"model-versions/{version_id}",
                                    f"model version info for ID {version_id}", hosts or hosts_to_try())
    
    async def search_models(self, session: aiohttp.ClientSession, query: str,
                            hosts: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """Search for models by name"""
        params = {
            'query': query,
            'limit': 10,
            'primaryFileOnly': 'true'
        }
        # A search that comes back empty on one host may still match on another
        result = None
        for host in hosts or hosts_to_try():
            data = await self._get_json(session, "models", f"search results for '{query}'", [host], params)
            if data is None:
                continue
            result = data.get('items', [])
            logger.debug(f"Search on {host} found {len(result)} models for query: {query}")
            if result:
                break
        return result
    
    def get_best_download_url(self, model_data: Dict[str, Any], preferred_version_id: Optional[str] = None) -> Optional[str]:
        """Extract the best download URL from model data"""
        model_versions = model_data.get('modelVersions', [])
        
        if not model_versions:
            logger.warning("No model versions found in model data")
            return None
        
        # If a specific version is requested, try to find it
        if preferred_version_id:
            for version in model_versions:
                if str(version.get('id')) == str(preferred_version_id):
                    download_url = version.get('downloadUrl')
                    if download_url:
                        logger.debug(f"Found download URL for specific version {preferred_version_id}")
                        return to_civitai_host(download_url, model_data.get(self.HOST_KEY))
        
        # Otherwise, use the first version (usually the latest)
        first_version = model_versions[0]
        download_url = first_version.get('downloadUrl')
        
        if download_url:
            logger.debug(f"Using download URL from first version: {first_version.get('id')}")
            return to_civitai_host(download_url, model_data.get(self.HOST_KEY))
        
        logger.warning("No download URL found in model versions")
        return None
    
    async def resolve_url(self, session: aiohttp.ClientSession, url: str, model_name: str = "") -> Tuple[bool, str]:
        """
        Resolve a URL to a proper download URL
        
        Returns:
            Tuple of (success, download_url_or_error_message)
        """
        url = self.sanitize_url(url)
        url_type, data = self.identify_url_type(url)
        hosts = hosts_to_try(url)
        
        logger.debug(f"Processing URL type '{url_type}' for: {url}")
        
        # If it's already a download URL, return as-is
        if url_type == 'download_url':
            logger.debug(f"URL is already a download URL: {url}")
            return True, url
        
        # Handle model version ID directly
        if url_type in ['model_version_page', 'query_version_id'] and 'model_version_id' in data:
            version_id = data['model_version_id']
            version_info = await self.get_model_version_info(session, version_id, hosts)
            
            if version_info:
                download_url = version_info.get('downloadUrl')
                if download_url:
                    download_url = to_civitai_host(download_url, version_info.get(self.HOST_KEY))
                    logger.success(f"Resolved version ID {version_id} to download URL")
                    return True, download_url
                else:
                    logger.warning(f"No download URL found for version ID {version_id}")
            else:
                logger.error(f"Could not fetch version info for ID {version_id}")
        
        # Handle model ID
        if url_type in ['model_page', 'model_id_only', 'query_model_id'] and 'model_id' in data:
            model_id = data['model_id']
            model_info = await self.get_model_info(session, model_id, hosts)
            
            if model_info:
                # Extract preferred version if available
                preferred_version = data.get('model_version_id')
                download_url = self.get_best_download_url(model_info, preferred_version)
                
                if download_url:
                    logger.success(f"Resolved model ID {model_id} to download URL")
                    return True, download_url
                else:
                    logger.warning(f"No download URL found for model ID {model_id}")
            else:
                logger.error(f"Could not fetch model info for ID {model_id}")
        
        # If we have a model name, try searching
        if model_name and url_type == 'unknown':
            logger.info(f"Attempting to search for model by name: {model_name}")
            search_results = await self.search_models(session, model_name, hosts)
            
            if search_results and len(search_results) > 0:
                # Use the first (most relevant) result
                first_result = search_results[0]
                download_url = self.get_best_download_url(first_result)
                
                if download_url:
                    logger.success(f"Found download URL via search for '{model_name}'")
                    return True, download_url
        
        # If all else fails
        error_msg = f"Could not resolve URL to download link: {url}"
        logger.error(error_msg)
        return False, error_msg
    
    @staticmethod
    def file_size_bytes(file: Optional[Dict[str, Any]]) -> Optional[int]:
        """Exact file size in bytes from CivitAI's sizeKB (bytes / 1024)"""
        size_kb = (file or {}).get('sizeKB')
        return round(size_kb * 1024) if size_kb else None
    
    @staticmethod
    def pick_primary_file(version_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Pick the file CivitAI serves by default for a model version"""
        files = version_data.get('files') or []
        for file in files:
            if file.get('primary'):
                return file
        return files[0] if files else None
    
    def pick_requested_file(self, version_data: Dict[str, Any], url: str) -> Optional[Dict[str, Any]]:
        """
        Pick the file a download link will serve
        
        Honours ?fileId= and ?type=/&format= on download links. Returns None when
        the link's options don't identify exactly one file.
        """
        files = version_data.get('files') or []
        query = parse_qs(urlparse(url).query) if self.url_patterns['download_url'].match(url) else {}
        
        if 'fileId' in query:
            return next((f for f in files if str(f.get('id')) == query['fileId'][0]), None)
        
        file_type = query.get('type', [None])[0]
        file_format = query.get('format', [None])[0]
        if file_type or file_format:
            matches = [
                f for f in files
                if (not file_type or str(f.get('type', '')).lower() == file_type.lower())
                and (not file_format or str((f.get('metadata') or {}).get('format', '')).lower() == file_format.lower())
            ]
            return matches[0] if len(matches) == 1 else None
        
        return self.pick_primary_file(version_data)
    
    async def resolve_download_target(self, session: aiohttp.ClientSession, url: str) -> Tuple[bool, Any]:
        """
        Resolve a URL/ID/name to everything needed to download it
        
        Returns:
            Tuple of (success, target_dict_or_error_message). The target dict contains
            download_url, model_id, model_version_id, model_name, version_name,
            model_type, file_name, file_size (bytes) and file_sha256 (any of which
            except download_url may be None).
        """
        url = self.sanitize_url(url)
        url_type, data = self.identify_url_type(url)
        hosts = hosts_to_try(url)
        logger.debug(f"Resolving download target for URL type '{url_type}': {url}")
        
        model_data: Optional[Dict[str, Any]] = None
        version_data: Optional[Dict[str, Any]] = None
        version_id = data.get('model_version_id')
        model_id = data.get('model_id')
        
        if version_id:
            version_data = await self.get_model_version_info(session, version_id, hosts)
        
        if version_data is None and model_id:
            model_data = await self.get_model_info(session, model_id, hosts)
            if model_data:
                versions = model_data.get('modelVersions') or []
                version_data = next(
                    (v for v in versions if version_id and str(v.get('id')) == str(version_id)),
                    versions[0] if versions else None
                )
        
        if version_data is None and model_data is None and url_type == 'unknown':
            # Only accept an exact name match, so stray words on the command line
            # (e.g. "download.py") can't download whatever the search ranks first
            search_results = await self.search_models(session, url, hosts) or []
            model_data = next(
                (m for m in search_results if m.get('name', '').strip().lower() == url.lower()),
                None
            )
            if model_data:
                versions = model_data.get('modelVersions') or []
                version_data = versions[0] if versions else None
            else:
                suggestions = ", ".join(f"'{m.get('name')}' ({m.get('id')})" for m in search_results[:3])
                error_msg = f"No model named '{url}' on CivitAI"
                if suggestions:
                    error_msg += f". Closest matches: {suggestions}. Pass a model ID or URL instead"
                logger.error(error_msg)
                return False, error_msg
        
        if version_data is None:
            # A direct download link still works without metadata
            if url_type == 'download_url':
                logger.warning(f"Could not fetch metadata for {url}, downloading as-is")
                return True, {
                    'download_url': to_civitai_host(url),
                    'model_id': None,
                    'model_version_id': version_id,
                    'model_name': None,
                    'version_name': None,
                    'model_type': None,
                    'file_name': None,
                    'file_size': None,
                    'file_sha256': None,
                }
            error_msg = f"Could not resolve URL to download link: {url}"
            logger.error(error_msg)
            return False, error_msg
        
        model_info = version_data.get('model') or {}
        requested_file = self.pick_requested_file(version_data, url)
        
        # The host that had the model, which is a fallback when it isn't on the link's own site
        found_on = (version_data.get(self.HOST_KEY) or (model_data or {}).get(self.HOST_KEY)
                    or host_of(version_data.get('downloadUrl')) or hosts[0])
        
        # Keep the user's own download link, since its query string can select a specific file
        if url_type == 'download_url':
            download_url = to_civitai_host(url, found_on)
        else:
            download_url = version_data.get('downloadUrl')
            if download_url:
                download_url = to_civitai_host(download_url, found_on)
            elif version_data.get('id'):
                download_url = download_url_for(version_data['id'], found_on)
        
        if not download_url:
            error_msg = f"No download URL found for: {url}"
            logger.error(error_msg)
            return False, error_msg
        
        target = {
            'download_url': download_url,
            'model_id': str(version_data.get('modelId') or (model_data or {}).get('id') or model_id or '') or None,
            'model_version_id': str(version_data.get('id') or version_id or '') or None,
            'model_name': model_info.get('name') or (model_data or {}).get('name'),
            'version_name': version_data.get('name'),
            'model_type': model_info.get('type') or (model_data or {}).get('type'),
            'file_name': requested_file.get('name') if requested_file else None,
            'file_size': self.file_size_bytes(requested_file),
            'file_sha256': ((requested_file or {}).get('hashes') or {}).get('SHA256'),
        }
        logger.success(f"Resolved {url} to {download_url}")
        return True, target
    
    async def process_csv_file(self, csv_path: Path, output_path: Optional[Path] = None) -> Tuple[int, int, int]:
        """
        Process a CSV file and resolve all URLs to download URLs
        
        Returns:
            Tuple of (total_processed, successfully_resolved, failed_to_resolve)
        """
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            return 0, 0, 0
        
        if output_path is None:
            output_path = csv_path
        
        logger.info(f"Processing CSV file: {csv_path}")
        
        # Read the CSV file
        rows = []
        headers = None
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                rows = list(reader)
        except Exception as e:
            logger.error(f"Error reading CSV file {csv_path}: {e}")
            return 0, 0, 0
        
        if not headers or not rows:
            logger.warning(f"CSV file is empty or has no data: {csv_path}")
            return 0, 0, 0
        
        logger.info(f"Found {len(rows)} rows to process")
        
        total_processed = 0
        successfully_resolved = 0
        failed_to_resolve = 0
        
        # Process URLs asynchronously
        async with aiohttp.ClientSession() as session:
            for i, row in enumerate(rows):
                if len(row) < 4:  # Need at least: SrNo, Model_ID, Model_Name, Model_URL
                    logger.warning(f"Row {i+1} has insufficient columns, skipping")
                    continue
                
                total_processed += 1
                sr_no, model_id, model_name, model_url = row[:4]
                
                logger.debug(f"Processing row {i+1}: {model_name} - {model_url}")
                
                success, result = await self.resolve_url(session, model_url, model_name)
                
                if success:
                    # Update the URL in the row
                    row[3] = result  # Update Model_URL column
                    successfully_resolved += 1
                    logger.info(f"✓ Resolved: {model_name}")
                else:
                    failed_to_resolve += 1
                    logger.warning(f"✗ Failed: {model_name} - {result}")
        
        # Write the updated CSV
        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            
            logger.success(f"Updated CSV saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error writing updated CSV to {output_path}: {e}")
        
        return total_processed, successfully_resolved, failed_to_resolve
        
    async def process_text_file(self, text_path: Path, output_path: Optional[Path] = None) -> Tuple[int, int, int]:
        """
        Process a text file containing mixed URLs/IDs/names and convert to CSV format
        
        Args:
            text_path: Path to text file containing URLs/IDs/names (one per line)
            output_path: Optional output path for CSV file
        
        Returns:
            Tuple of (total_processed, successfully_resolved, failed_to_resolve)
        """
        if not text_path.exists():
            logger.error(f"Text file not found: {text_path}")
            return 0, 0, 0
        
        if output_path is None:
            # Generate CSV filename from text file name
            output_path = text_path.with_suffix('.csv')
        
        logger.info(f"Processing text file: {text_path}")
        
        # Read the text file
        lines = []
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            logger.error(f"Error reading text file {text_path}: {e}")
            return 0, 0, 0
        
        if not lines:
            logger.warning(f"Text file is empty: {text_path}")
            return 0, 0, 0
        
        logger.info(f"Found {len(lines)} entries to process")
        
        total_processed = 0
        successfully_resolved = 0
        failed_to_resolve = 0
        
        # Prepare CSV data
        csv_rows = []
        
        # Process each line asynchronously
        async with aiohttp.ClientSession() as session:
            for i, line in enumerate(lines):
                if not line:
                    continue
                
                total_processed += 1
                
                logger.debug(f"Processing line {i+1}: {line}")
                
                # Try to resolve the URL/ID/name
                success, result = await self.resolve_url(session, line, line)
                
                if success:
                    # Extract model name if possible
                    model_name = await self.extract_model_name(session, result, line)
                    
                    # Create CSV row: SrNo, Model_ID, Model_Name, Model_URL
                    csv_row = [
                        str(i + 1),  # SrNo
                        self.extract_model_id_from_url(result) or "Unknown",  # Model_ID
                        model_name or f"Model_{i+1}",  # Model_Name
                        result  # Model_URL (download URL)
                    ]
                    csv_rows.append(csv_row)
                    successfully_resolved += 1
                    logger.info(f"✓ Resolved: {line}")
                else:
                    # Add failed entry with original data
                    csv_row = [
                        str(i + 1),  # SrNo
                        "Failed",  # Model_ID
                        line,  # Model_Name (use original input)
                        line  # Model_URL (keep original for manual review)
                    ]
                    csv_rows.append(csv_row)
                    failed_to_resolve += 1
                    logger.warning(f"✗ Failed: {line} - {result}")
        
        # Write the CSV file
        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['SrNo', 'Model_ID', 'Model_Name', 'Model_URL'])
                # Write data rows
                writer.writerows(csv_rows)
            
            logger.success(f"CSV file created: {output_path}")
        except Exception as e:
            logger.error(f"Error writing CSV to {output_path}: {e}")
        
        return total_processed, successfully_resolved, failed_to_resolve
    
    def extract_model_id_from_url(self, url: str) -> Optional[str]:
        """Extract model ID from a download URL"""
        match = self.url_patterns['download_url'].match(url)
        if match:
            return match.group(1)
        return None
    
    async def extract_model_name(self, session: aiohttp.ClientSession, download_url: str, original_input: str) -> Optional[str]:
        """Try to extract model name from download URL or return original input"""
        # If original input looks like a name (not URL or ID), use it
        if not (original_input.startswith('http') or original_input.isdigit()):
            return original_input
        
        # Try to get model name from API using the download URL
        model_id = self.extract_model_id_from_url(download_url)
        if model_id:
            model_info = await self.get_model_info(session, model_id)
            if model_info:
                return model_info.get('name', f"Model_{model_id}")
        
        return None


    async def process_directory(self, csv_dir: Path) -> Dict[str, Tuple[int, int, int]]:
        """
        Process all CSV files in a directory
        
        Returns:
            Dict mapping filename to (total_processed, successfully_resolved, failed_to_resolve)
        """
        if not csv_dir.exists():
            logger.error(f"CSV directory not found: {csv_dir}")
            return {}
        
        csv_files = list(csv_dir.glob("*.csv"))
        if not csv_files:
            logger.warning(f"No CSV files found in directory: {csv_dir}")
            return {}
        
        logger.info(f"Found {len(csv_files)} CSV files to process")
        
        results = {}
        for csv_file in csv_files:
            if csv_file.name.lower() in ['template.csv', '_csv files go here.txt']:
                logger.info(f"Skipping template file: {csv_file.name}")
                continue
            
            logger.info(f"Processing: {csv_file.name}")
            result = await self.process_csv_file(csv_file)
            results[csv_file.name] = result
        
        return results
    
    async def process_mixed_directory(self, input_dir: Path) -> Dict[str, Tuple[int, int, int]]:
        """
        Process all CSV and text files in a directory
        
        Returns:
            Dict mapping filename to (total_processed, successfully_resolved, failed_to_resolve)
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return {}
        
        # Find CSV and text files
        csv_files = list(input_dir.glob("*.csv"))
        txt_files = list(input_dir.glob("*.txt"))
        
        if not csv_files and not txt_files:
            logger.warning(f"No CSV or text files found in directory: {input_dir}")
            return {}
        
        logger.info(f"Found {len(csv_files)} CSV files and {len(txt_files)} text files to process")
        
        results = {}
        
        # Process CSV files
        for csv_file in csv_files:
            if csv_file.name.lower() in ['template.csv', '_csv files go here.txt']:
                logger.info(f"Skipping template file: {csv_file.name}")
                continue
            
            logger.info(f"Processing CSV: {csv_file.name}")
            result = await self.process_csv_file(csv_file)
            results[csv_file.name] = result
        
        # Process text files
        for txt_file in txt_files:
            if txt_file.name.lower() in ['_csv files go here.txt']:
                logger.info(f"Skipping info file: {txt_file.name}")
                continue
            
            logger.info(f"Processing text file: {txt_file.name}")
            result = await self.process_text_file(txt_file)
            results[f"{txt_file.name} -> {txt_file.stem}.csv"] = result
        
        return results


async def process_single_url(url: str, api_key: Optional[str] = None) -> Tuple[bool, str, Dict[str, str]]:
    """
    Process a single URL and return download URL with metadata
    
    Args:
        url: The URL/ID/name to process
        api_key: CivitAI API key for authentication
    
    Returns:
        Tuple of (success, download_url_or_error, metadata_dict)
    """
    preprocessor = URLPreprocessor(api_key)
    
    async with aiohttp.ClientSession() as session:
        success, target = await preprocessor.resolve_download_target(session, url)
        
        if not success:
            return False, target, {}
        
        result = target['download_url']
        metadata = {
            key: value for key, value in {
                'model_id': target['model_id'],
                'model_version_id': target['model_version_id'],
                'model_name': target['model_name'],
                'version_name': target['version_name'],
                'model_type': target['model_type'],
                'file_name': target['file_name'],
                'download_url': result,
            }.items() if value
        }
        
        return success, result, metadata


async def preprocess_urls(api_key: Optional[str] = None, csv_dir: Optional[Path] = None, include_text_files: bool = True) -> Dict[str, Tuple[int, int, int]]:
    """
    Main function to preprocess URLs in CSV files and optionally text files
    
    Args:
        api_key: CivitAI API key for authentication
        csv_dir: Directory containing CSV/text files (defaults to CSVs)
        include_text_files: Whether to process .txt files as well
    
    Returns:
        Dict mapping filename to processing results
    """
    if csv_dir is None:
        csv_dir = Path.cwd() / "CSVs"
    
    preprocessor = URLPreprocessor(api_key)
    
    if include_text_files:
        return await preprocessor.process_mixed_directory(csv_dir)
    else:
        return await preprocessor.process_directory(csv_dir)


if __name__ == "__main__":
    # Example usage
    import sys
    
    async def main():
        # You can provide an API key as a command line argument
        api_key = sys.argv[1] if len(sys.argv) > 1 else None
        
        if not api_key:
            print("Warning: No API key provided. Some protected models may not be accessible.")
            print("Usage: python preprocess.py [API_KEY]")
        
        results = await preprocess_urls(api_key)
        
        print("\n=== URL Preprocessing Results ===")
        total_all = 0
        success_all = 0
        failed_all = 0
        
        for filename, (total, success, failed) in results.items():
            print(f"\n{filename}:")
            print(f"  Total processed: {total}")
            print(f"  Successfully resolved: {success}")
            print(f"  Failed to resolve: {failed}")
            
            total_all += total
            success_all += success
            failed_all += failed
        
        print(f"\n=== Overall Summary ===")
        print(f"Total URLs processed: {total_all}")
        print(f"Successfully resolved: {success_all}")
        print(f"Failed to resolve: {failed_all}")
        
        if total_all > 0:
            success_rate = (success_all / total_all) * 100
            print(f"Success rate: {success_rate:.1f}%")
    
    asyncio.run(main())
