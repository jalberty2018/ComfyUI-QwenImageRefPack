"""Image thumbnail and input-list routes used by the copied MiniMax canvas UI."""
from __future__ import annotations

import os

from aiohttp import web

from . import media
from .refs import ReferenceError, _crop, reference_path

try:
    import folder_paths
    from server import PromptServer
except ImportError:  # pragma: no cover - ComfyUI-only integration
    folder_paths = None
    PromptServer = None


def _rotation(raw: str | None) -> int:
    try:
        value = int(raw or 0)
    except ValueError as exc:
        raise ReferenceError("rotate must be 0, 90, 180, or 270") from exc
    if value not in (0, 90, 180, 270):
        raise ReferenceError("rotate must be 0, 90, 180, or 270")
    return value


async def thumb_route(request: web.Request) -> web.Response:
    try:
        path = reference_path(folder_paths.get_input_directory(), request.query.get("file", ""))
        if not path.is_file():
            return web.Response(status=404)
        crop = _crop([float(part) for part in request.query["crop"].split(",")]) if "crop" in request.query else None
        rotation = _rotation(request.query.get("rotate"))
        mirror = request.query.get("mirror") == "1"
        return web.Response(
            body=media.thumbnail_png(str(path), crop=crop, rotation=rotation, mirror=mirror),
            content_type="image/png",
        )
    except (ReferenceError, ValueError):
        return web.Response(status=400)


async def list_files_route(request: web.Request) -> web.Response:
    if request.query.get("kind") != "image":
        return web.Response(status=400, text="kind must be image")
    input_dir = folder_paths.get_input_directory()
    files = [name for name in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, name))]
    return web.json_response({"files": folder_paths.filter_files_content_types(files, ["image"])})


if PromptServer is not None:  # pragma: no branch - true in ComfyUI
    PromptServer.instance.routes.get("/qwen_image_refpack/thumb")(thumb_route)
    PromptServer.instance.routes.get("/qwen_image_refpack/files")(list_files_route)
