"""
CivitAI host configuration
"""

import re
from typing import List, Optional

# CivitAI sites that serve the API. civitai.red carries NSFW models and
# civitai.com doesn't. A link keeps its own host, and a model missing there is
# looked up on the other one.
CIVITAI_HOSTS = (
    "https://civitai.red",
    "https://civitai.com",
)

# Older names that redirect to one of the sites above
CIVITAI_HOST_ALIASES = {"green": "com"}

# Host used when the input has no host of its own (a bare model ID or name)
CIVITAI_HOST = CIVITAI_HOSTS[0]
CIVITAI_API_BASE = f"{CIVITAI_HOST}/api/v1"

# Hosts accepted in user-supplied links
CIVITAI_HOST_PATTERN = r'https?://(?:www\.)?civitai\.(?:com|red|green)'

_HOST_RE = re.compile(rf'^{CIVITAI_HOST_PATTERN}(?=/|$)')
_TLD_RE = re.compile(r'^https?://(?:www\.)?civitai\.(com|red|green)(?=/|$)')


def host_of(url: Optional[str]) -> Optional[str]:
    """The CivitAI host a link points at, as https://civitai.<tld>, or None"""
    match = _TLD_RE.match((url or "").strip())
    if not match:
        return None
    tld = match.group(1)
    return f"https://civitai.{CIVITAI_HOST_ALIASES.get(tld, tld)}"


def hosts_to_try(url: Optional[str] = None) -> List[str]:
    """The link's own host first, then the other CivitAI hosts"""
    first = host_of(url) or CIVITAI_HOST
    return [first] + [host for host in CIVITAI_HOSTS if host != first]


def api_base(host: str = CIVITAI_HOST) -> str:
    """API root on a CivitAI host"""
    return f"{host}/api/v1"


def download_url_for(version_id, host: str = CIVITAI_HOST) -> str:
    """Build the download URL for a model version"""
    return f"{host}/api/download/models/{version_id}"


def to_civitai_host(url: str, host: Optional[str] = None) -> str:
    """
    Normalise a CivitAI link to https without "www.", on the given host

    Without a host the link stays on its own site. Links that aren't on a
    CivitAI host are returned unchanged.
    """
    url = url.strip()
    target = host or host_of(url)
    if not target:
        return url
    return _HOST_RE.sub(target, url, count=1)
