"""Jupyter Server extension: make folders named "checkpoints" browsable.

Jupyter Server routes every ``/api/contents/<path>/checkpoints`` URL to its
notebook-checkpoint API before the generic contents handler gets a chance, so
a real directory called ``checkpoints`` (e.g. ``ComfyUI/models/checkpoints``)
cannot be opened in the JupyterLab file browser.

This extension inserts one routing rule ahead of the defaults: when the
requested path (ending in ``/checkpoints`` or ``/checkpoints/<name>``) exists
on disk as a file or directory, the request is served by the normal
``ContentsHandler``. Anything else still falls through to the checkpoint API,
so notebook checkpoints keep working.
"""

import inspect
import os

from jupyter_server.services.contents.handlers import ContentsHandler
from jupyter_server.utils import url_path_join
from tornado.routing import PathMatches, Rule

_PATTERN = r"/api/contents(?P<path>(?:/[^/]+)*/checkpoints(?:/[^/]+)?)"


def _exists(contents_manager, path):
    """True if ``path`` (API path) is an existing file or directory."""
    root_dir = getattr(contents_manager, "root_dir", None)
    if root_dir:
        os_path = os.path.join(root_dir, *path.strip("/").split("/"))
        return os.path.lexists(os_path)
    for check in (contents_manager.dir_exists, contents_manager.file_exists):
        result = check(path)
        if inspect.isawaitable(result):
            # Async contents manager without a local root_dir: cannot decide
            # synchronously, so leave the request to the default routing.
            result.close()
            return False
        if result:
            return True
    return False


class ExistingPathMatches(PathMatches):
    """Match the pattern only when the captured path exists on disk."""

    def __init__(self, pattern, contents_manager):
        super().__init__(pattern)
        self.contents_manager = contents_manager

    def match(self, request):
        matched = super().match(request)
        if matched is None:
            return None
        path = matched["path_kwargs"]["path"]
        if isinstance(path, bytes):
            path = path.decode("utf-8", "surrogateescape")
        if _exists(self.contents_manager, path):
            return matched
        return None


def _jupyter_server_extension_points():
    return [{"module": "jupyter_checkpoints_dir_fix"}]


def _load_jupyter_server_extension(serverapp):
    web_app = serverapp.web_app
    pattern = url_path_join(web_app.settings["base_url"], _PATTERN)
    matcher = ExistingPathMatches(pattern, serverapp.contents_manager)
    router = web_app.wildcard_router
    router.rules.insert(0, router.process_rule(Rule(matcher, ContentsHandler)))
    serverapp.log.info("jupyter_checkpoints_dir_fix: folders named 'checkpoints' are browsable")


# Backwards-compatible alias used by older jupyter_server versions.
load_jupyter_server_extension = _load_jupyter_server_extension
