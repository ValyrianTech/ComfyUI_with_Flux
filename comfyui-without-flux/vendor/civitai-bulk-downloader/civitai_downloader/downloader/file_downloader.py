"""
Async file downloader with retry logic and progress tracking
"""

import asyncio
import hashlib
import re
import shutil
import aiofiles
import aiohttp
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import unquote
from tqdm.asyncio import tqdm
from loguru import logger
import threading

from ..config.urls import host_of, hosts_to_try, to_civitai_host


class ProgressManager:
    """Manages multiple concurrent progress bars"""
    
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self.active_downloads = {}
        self.next_position = 1
        self.lock = threading.Lock()
        self.overall_pbar = None  # type: Optional[tqdm]
    
    def create_file_progress(self, file_id: str, filename: str, total_size: int) -> tqdm:
        """Create a progress bar for a specific file"""
        with self.lock:
            position = self.next_position
            self.next_position += 1
            
            if total_size > 0:
                pbar = tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"📥 {filename[:35]}",
                    position=position,
                    leave=False,
                    bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
                )
            else:
                pbar = tqdm(
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"📥 {filename[:35]}",
                    position=position,
                    leave=False,
                    bar_format="{desc}: {n_fmt} [{elapsed}, {rate_fmt}]"
                )
            
            self.active_downloads[file_id] = pbar
            return pbar
    
    def remove_file_progress(self, file_id: str):
        """Remove a file's progress bar"""
        with self.lock:
            if file_id in self.active_downloads:
                self.active_downloads[file_id].close()
                del self.active_downloads[file_id]
    
    def cleanup(self):
        """Clean up all progress bars"""
        with self.lock:
            for pbar in self.active_downloads.values():
                pbar.close()
            self.active_downloads.clear()
            if self.overall_pbar:
                self.overall_pbar.close()


class FileDownloader:
    """Handles async file downloads with retry logic"""
    
    # Progress line printed by aria2c with --human-readable=false, e.g. "[#2089b0 4194304B/23802920805B(0%) CN:16 DL:..."
    ARIA2_PROGRESS_RE = re.compile(r'\[#\w+ (\d+)B/(\d+)B')
    # Row of aria2c's "Download Results" table, e.g. "2089b0|OK  |  42MiB/s|100|/path/to/file"
    ARIA2_RESULT_RE = re.compile(r'^\w+\|(OK|ERR|INPR|RM)\s*\|[^|]*\|[^|]*\|(.+)$')
    # aria2c exit codes worth explaining (see "EXIT STATUS" in the aria2c manual)
    ARIA2_EXIT_CODES = {
        3: "File not found",
        9: "Not enough disk space",
        24: "Authentication failed. Check your API key",
        32: "Checksum (SHA256) does not match CivitAI's hash",
    }
    
    def __init__(self, api_key: Optional[str] = None, download_settings: Optional[Dict] = None):
        self.api_key = api_key
        self.download_settings = download_settings or {
            "max_concurrent_downloads": 4,
            "timeout": 30,
            "retry_attempts": 3
        }
        self.session: Optional[aiohttp.ClientSession] = None
        self.aria2_path = self.find_aria2()
    
    def find_aria2(self) -> Optional[str]:
        """Path to aria2c when it is installed and enabled ("use_aria2": true/false/"auto")"""
        use_aria2 = self.download_settings.get("use_aria2", "auto")
        if use_aria2 is False or str(use_aria2).lower() in ("false", "no", "off"):
            return None
        path = shutil.which("aria2c")
        if not path and use_aria2 is True:
            logger.warning("aria2c is not installed, falling back to the built-in downloader")
        return path
    
    async def __aenter__(self):
        # No total limit: large models take far longer than any fixed timeout.
        # "timeout" applies to connecting, "read_timeout" to a transfer stalling.
        connect_timeout = self.download_settings.get("timeout", 30)
        read_timeout = self.download_settings.get("read_timeout", 300)
        timeout = aiohttp.ClientTimeout(total=None, sock_connect=connect_timeout, sock_read=read_timeout)
        connector = aiohttp.TCPConnector(limit=self.download_settings.get("max_concurrent_downloads", 4))
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def add_api_key_to_url(self, url: str) -> str:
        """Add API key to URL if not using headers"""
        if not self.api_key:
            return url
        
        if "?" in url:
            return f"{url}&token={self.api_key}"
        else:
            return f"{url}?token={self.api_key}"
    
    def redact(self, text: str) -> str:
        """Hide the API key in messages that may include a request URL"""
        return text.replace(self.api_key, "***") if self.api_key else text
    
    @staticmethod
    def filename_from_content_disposition(content_disposition: str) -> Optional[str]:
        """Extract a safe file name from a Content-Disposition header"""
        match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', content_disposition, re.IGNORECASE)
        if not match:
            return None
        name = Path(unquote(match.group(1).strip())).name
        return name or None
    
    @staticmethod
    def sha256_of(file_path: Path) -> str:
        """Compute a file's SHA256 hash"""
        digest = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                digest.update(block)
        return digest.hexdigest().upper()
    
    @staticmethod
    def partial_markers(file_path: Path) -> List[Path]:
        """Files that mark an unfinished download: our .part file and aria2's .aria2 control file"""
        return [file_path.with_name(file_path.name + ".part"),
                file_path.with_name(file_path.name + ".aria2")]
    
    async def check_existing_file(self, file_path: Path, expected_size: Optional[int],
                                  expected_sha256: Optional[str]) -> Optional[str]:
        """
        Decide whether an existing file is complete
        
        Returns a skip message if the file is complete, or None if it must be
        (re)downloaded. Files whose expected size is unknown are not judged here.
        """
        if file_path.with_name(file_path.name + ".aria2").exists():
            logger.info(f"{file_path.name} has an unfinished aria2 download, resuming")
            return None
        
        actual_size = file_path.stat().st_size
        if expected_size is not None and actual_size != expected_size:
            logger.warning(f"{file_path.name} is {actual_size} bytes but should be {expected_size}, re-downloading")
            return None
        
        if expected_sha256 and self.download_settings.get("verify_hash", False):
            actual_sha256 = await asyncio.to_thread(self.sha256_of, file_path)
            if actual_sha256 != expected_sha256.upper():
                logger.warning(f"{file_path.name} hash does not match CivitAI's, re-downloading")
                return None
        
        logger.info(f"File already exists and is complete, skipping: {file_path.name}")
        return f"Skipped (already exists): {file_path.name}"
    
    async def download_file(self, url: str, file_path: Path, semaphore: asyncio.Semaphore, 
                          progress_manager: ProgressManager,
                          expected: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Download a single file with retry logic, resume support and progress tracking
        
        Uses aria2c (several connections per file) when it is installed, otherwise
        the built-in downloader.
        
        Args:
            expected: Optional {"size": bytes, "sha256": hex} from CivitAI metadata
        """
        expected = expected or {}
        expected_size = expected.get("size")
        expected_sha256 = expected.get("sha256")
        
        # Check if file already exists (if skip_existing_files is enabled)
        skip_existing = self.download_settings.get("skip_existing_files", True)
        checked_path = None
        if skip_existing and file_path.exists() and expected_size is not None:
            checked_path = file_path
            skip_message = await self.check_existing_file(file_path, expected_size, expected_sha256)
            if skip_message:
                return True, skip_message
        
        # A link missing on its own CivitAI site may still be on one of the others
        request_urls = [to_civitai_host(url, host) for host in hosts_to_try(url)] if host_of(url) else [url]
        
        async with semaphore:
            for index, request_url in enumerate(request_urls):
                if self.aria2_path:
                    success, message = await self._download_with_aria2(request_url, file_path, progress_manager,
                                                                       expected_size, expected_sha256)
                else:
                    success, message = await self._download_with_aiohttp(request_url, file_path, progress_manager,
                                                                         expected_size, expected_sha256, checked_path)
                if success or not message.startswith("File not found") or index == len(request_urls) - 1:
                    return success, message
                logger.info(f"{file_path.name} not found on {host_of(request_url)}, "
                            f"trying {host_of(request_urls[index + 1])}")
            return success, message
    
    async def _download_with_aria2(self, url: str, file_path: Path, progress_manager: ProgressManager,
                                   expected_size: Optional[int], expected_sha256: Optional[str]) -> Tuple[bool, str]:
        """Download one file with aria2c, splitting it over several connections"""
        file_id = f"{file_path.name}_{id(asyncio.current_task())}"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        connections = max(1, min(16, int(self.download_settings.get("aria2_connections", 16))))
        verify = expected_sha256 and self.download_settings.get("verify_hash", False)
        
        # The file name is only known up front for links resolved through the API;
        # otherwise aria2c takes it from the server like the built-in downloader does
        name_known = expected_size is not None
        if name_known:
            part_path = file_path.with_name(file_path.name + ".part")
            if part_path.exists() and not file_path.exists():
                # Continue a download the built-in downloader started (written sequentially)
                part_path.replace(file_path)
            elif file_path.exists() and file_path.stat().st_size > expected_size:
                file_path.unlink()
        
        # The key goes in the URL instead of a header so it isn't forwarded to the
        # storage host CivitAI redirects to, and in the input file so it stays out
        # of the process list
        entry = [self.add_api_key_to_url(to_civitai_host(url)), f"  dir={file_path.parent}"]
        if name_known:
            entry.append(f"  out={file_path.name}")
        if verify:
            entry.append(f"  checksum=sha-256={expected_sha256.lower()}")
        
        retry_attempts = self.download_settings.get("retry_attempts", 3)
        args = [
            self.aria2_path, "--input-file=-",
            f"--max-connection-per-server={connections}", f"--split={connections}", "--min-split-size=1M",
            "--continue=true", "--auto-file-renaming=false", "--allow-overwrite=true",
            "--file-allocation=none", "--content-disposition-default-utf8=true",
            f"--max-tries={max(5, retry_attempts * 5)}", "--retry-wait=10",
            f"--timeout={self.download_settings.get('read_timeout', 300)}",
            f"--connect-timeout={self.download_settings.get('timeout', 30)}",
            "--summary-interval=1", "--human-readable=false", "--show-console-readout=false",
            "--console-log-level=warn", "--download-result=full",
            *self.download_settings.get("aria2_args", []),
        ]
        
        logger.debug(f"Starting aria2c download ({connections} connections): {file_path.name}")
        progress = progress_manager.create_file_progress(file_id, file_path.name, expected_size or 0)
        result_status = None
        result_path = None
        errors = []
        try:
            process = await asyncio.create_subprocess_exec(
                *args, stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
            )
            process.stdin.write(("\n".join(entry) + "\n").encode())
            await process.stdin.drain()
            process.stdin.close()
            
            async for raw_line in process.stdout:
                line = raw_line.decode(errors="replace").strip()
                progress_match = self.ARIA2_PROGRESS_RE.search(line)
                if progress_match:
                    done, total = int(progress_match.group(1)), int(progress_match.group(2))
                    if total and progress.total != total:
                        progress.total = total
                    progress.update(done - progress.n)
                    continue
                result_match = self.ARIA2_RESULT_RE.match(line)
                if result_match:
                    result_status, result_path = result_match.group(1), result_match.group(2).strip()
                elif "[ERROR]" in line or "[WARN]" in line or "errorCode" in line:
                    errors.append(self.redact(line))
                    logger.debug(f"aria2c: {self.redact(line)}")
            
            return_code = await process.wait()
        except (OSError, asyncio.CancelledError) as e:
            return False, f"Error running aria2c for {url}: {e}"
        finally:
            progress_manager.remove_file_progress(file_id)
        
        if return_code == 32 and name_known and file_path.exists():
            # A full-size file with the wrong hash must not look finished next time
            file_path.unlink()
        
        if return_code != 0 or result_status != "OK":
            reason = self.ARIA2_EXIT_CODES.get(return_code)
            detail = errors[-1] if errors else f"aria2c exited with code {return_code}"
            if reason:
                return False, f"{reason} for {url} ({detail})"
            return False, f"Error downloading {url}: {detail}"
        
        final_path = Path(result_path) if result_path and not result_path.startswith("http") else file_path
        if expected_size is not None and final_path.exists() and final_path.stat().st_size != expected_size:
            return False, (f"Error downloading {url}: incomplete download "
                           f"({final_path.stat().st_size} of {expected_size} bytes)")
        
        logger.success(f"Successfully downloaded: {final_path.name}")
        return True, f"Downloaded: {final_path.name}"
    
    async def _download_with_aiohttp(self, url: str, file_path: Path, progress_manager: ProgressManager,
                                     expected_size: Optional[int], expected_sha256: Optional[str],
                                     checked_path: Optional[Path]) -> Tuple[bool, str]:
        """
        Download one file over a single connection
        
        Data is written to "<name>.part" and only renamed once the size (and,
        with verify_hash, the SHA256) matches. Every attempt resumes from the
        bytes already in the .part file, and attempts that make progress don't
        count towards retry_attempts, so a long download survives any number of
        dropped connections as long as it keeps moving.
        """
        file_id = f"{file_path.name}_{id(asyncio.current_task())}"
        skip_existing = self.download_settings.get("skip_existing_files", True)
        retry_attempts = self.download_settings.get("retry_attempts", 3)
        request_url = to_civitai_host(url)
        download_url = request_url if self.api_key else self.add_api_key_to_url(request_url)
        
        failures = 0
        attempt = 0
        while True:
            attempt += 1
            part_path = file_path.with_name(file_path.name + ".part")
            resume_from = part_path.stat().st_size if part_path.exists() else 0
            if expected_size is not None and resume_from > expected_size:
                part_path.unlink()
                resume_from = 0
            
            headers = {"Range": f"bytes={resume_from}-"} if resume_from else {}
            bytes_before = resume_from
            try:
                if resume_from:
                    logger.info(f"Resuming {file_path.name} from {resume_from} bytes")
                
                async with self.session.get(download_url, headers=headers) as response: # type: ignore
                    if response.status == 401:
                        return False, f"Authentication failed for {url}. Check your API key."
                    if response.status == 404:
                        return False, f"File not found: {url}"
                    if response.status == 416 and expected_size is not None and resume_from == expected_size:
                        pass  # The .part file already holds everything
                    elif response.status not in (200, 206):
                        raise aiohttp.ClientResponseError(
                            response.request_info, response.history,
                            status=response.status, message=f"HTTP {response.status} for {url}"
                        )
                    else:
                        server_name = self.filename_from_content_disposition(
                            response.headers.get('content-disposition', '')
                        )
                        if server_name and server_name != file_path.name:
                            # The server's name wins; carry on with that name's .part file instead
                            file_path = file_path.parent / server_name
                            if response.status == 206:
                                continue
                        
                        if expected_size is None and response.content_length:
                            expected_size = response.content_length + (resume_from if response.status == 206 else 0)
                        
                        # Now that the real name and size are known, check for a finished file
                        if skip_existing and file_path.exists() and file_path != checked_path:
                            checked_path = file_path
                            skip_message = await self.check_existing_file(file_path, expected_size, expected_sha256)
                            if skip_message:
                                return True, skip_message
                        
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        part_path = file_path.with_name(file_path.name + ".part")
                        if response.status == 206:
                            await self._write_body(response, part_path, 'ab', resume_from, expected_size,
                                                   file_id, file_path.name, progress_manager)
                        else:
                            # Full body (first attempt, or the server ignored the Range request)
                            await self._write_body(response, part_path, 'wb', 0, expected_size,
                                                   file_id, file_path.name, progress_manager)
                
                actual_size = part_path.stat().st_size
                if expected_size is not None and actual_size != expected_size:
                    raise IOError(f"incomplete download ({actual_size} of {expected_size} bytes)")
                
                if expected_sha256 and self.download_settings.get("verify_hash", False):
                    actual_sha256 = await asyncio.to_thread(self.sha256_of, part_path)
                    if actual_sha256 != expected_sha256.upper():
                        part_path.unlink()
                        raise IOError("SHA256 does not match CivitAI's hash")
                
                part_path.replace(file_path)
                logger.success(f"Successfully downloaded: {file_path.name}")
                return True, f"Downloaded: {file_path.name}"
            
            except asyncio.TimeoutError:
                error_msg = f"Timeout downloading {url} (no data for {self.download_settings.get('read_timeout', 300)}s)"
            except aiohttp.ClientResponseError as e:
                error_msg = e.message or f"HTTP {e.status} for {url}"
            except Exception as e:
                error_msg = f"Error downloading {url}: {str(e)}"
            
            bytes_after = part_path.stat().st_size if part_path.exists() else 0
            if bytes_after > bytes_before:
                failures = 0  # Progress was made, so this doesn't count as a failed try
            else:
                failures += 1
            
            logger.warning(f"Attempt {attempt} for {file_path.name} stopped: {self.redact(error_msg)} "
                           f"({bytes_after} bytes so far)")
            if failures >= retry_attempts:
                return False, self.redact(error_msg)
            await asyncio.sleep(min(2 ** failures, 30))
    
    async def _write_body(self, response, part_path: Path, mode: str, already: int,
                          expected_size: Optional[int], file_id: str, display_name: str,
                          progress_manager: ProgressManager):
        """Stream a response body into part_path with a progress bar"""
        progress = progress_manager.create_file_progress(file_id, display_name, expected_size or 0)
        if already:
            progress.update(already)
        try:
            async with aiofiles.open(part_path, mode) as f:
                # iter_any yields data as it arrives, so bytes received before a drop are kept
                async for chunk in response.content.iter_any():
                    await f.write(chunk)
                    progress.update(len(chunk))
        finally:
            progress_manager.remove_file_progress(file_id)
    
    async def download_files(self, download_tasks: List[Tuple], 
                           progress_desc: str = "Downloading") -> List[Tuple[bool, str]]:
        """Download multiple files with concurrent progress tracking"""
        if not download_tasks:
            return []
        
        logger.info(f"Starting batch download of {len(download_tasks)} files")
        max_concurrent = self.download_settings.get("max_concurrent_downloads", 4)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create progress manager for concurrent downloads
        progress_manager = ProgressManager(max_concurrent)
        
        if self.aria2_path:
            connections = max(1, min(16, int(self.download_settings.get("aria2_connections", 16))))
            engine = f"aria2c, {connections} connections per file"
        else:
            engine = "built-in downloader; install aria2c for faster multi-connection downloads"
        print(f"Starting download of {len(download_tasks)} files (max {max_concurrent} concurrent, {engine})...")
        
        try:
            # Create download tasks with progress manager
            tasks = []
            for url, file_path, *rest in download_tasks:
                # Tasks may carry a third item: {"size": bytes, "sha256": hex} to verify against
                extra = {"expected": rest[0]} if rest and rest[0] else {}
                task = self.download_file(url, file_path, semaphore, progress_manager, **extra)
                tasks.append(task)
            
            # Execute downloads with overall progress bar
            results = []
            successful_count = 0
            failed_count = 0
            skipped_count = 0
            
            # Enhanced overall progress bar
            progress_manager.overall_pbar = tqdm(
                total=len(tasks), 
                desc=f"🔄 {progress_desc}",
                unit="files",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}",
                position=0
            )
            
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                
                # Update counters based on result
                if result[0]:  # Success
                    if "Skipped" in result[1]:
                        skipped_count += 1
                    else:
                        successful_count += 1
                else:  # Failed
                    failed_count += 1
                
                # Update overall progress bar with current stats
                progress_manager.overall_pbar.set_postfix_str(f"✅{successful_count} ⏭️{skipped_count} ❌{failed_count}")
                progress_manager.overall_pbar.update(1)
        
        finally:
            # Clean up all progress bars
            progress_manager.cleanup()
        
        successful = sum(1 for success, message in results if success and "Skipped" not in message)
        skipped = sum(1 for success, message in results if success and "Skipped" in message)
        failed = sum(1 for success, _ in results if not success)
        logger.info(f"Batch download completed: {successful} downloaded, {skipped} skipped, {failed} failed")
        
        return results
