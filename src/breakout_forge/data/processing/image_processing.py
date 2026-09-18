"""Decode and preprocess image-stage assets in the Data layer."""

from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from breakout_forge.contracts.image_asset import PreparedImageAsset
from breakout_forge.contracts.settings import BreakImageSettings
from breakout_forge.contracts.stage import StageLayerDefinition


class ImageAssetError(ValueError):
    """Raised when a stage image cannot be decoded or prepared."""


def _channel_close(a: tuple[int, int, int], b: tuple[int, int, int], tolerance: int) -> bool:
    return max(abs(a[index] - b[index]) for index in range(3)) <= tolerance


def _remove_corner_background(image: Image.Image, tolerance: int) -> Image.Image:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int, tuple[int, int, int]]] = deque()

    corners = {
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    }
    for x, y in corners:
        r, g, b, a = pixels[x, y]
        queue.append((x, y, (r, g, b)))
        if a == 0:
            visited.add((x, y))

    while queue:
        x, y, seed = queue.popleft()
        if (x, y) in visited:
            continue
        r, g, b, a = pixels[x, y]
        if a != 0 and not _channel_close((r, g, b), seed, tolerance):
            continue
        visited.add((x, y))
        pixels[x, y] = (r, g, b, 0)
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny, seed))
    return rgba


def _active_tiles(
    image: Image.Image,
    *,
    columns: int,
    rows: int,
) -> frozenset[tuple[int, int]]:
    alpha = image.getchannel("A")
    active: set[tuple[int, int]] = set()
    for row in range(rows):
        y0 = row * image.height // rows
        y1 = (row + 1) * image.height // rows
        for column in range(columns):
            x0 = column * image.width // columns
            x1 = (column + 1) * image.width // columns
            if x1 <= x0 or y1 <= y0:
                continue
            if alpha.crop((x0, y0, x1, y1)).getbbox() is not None:
                active.add((column, row))
    return frozenset(active)


def prepare_image_asset(
    layer: StageLayerDefinition,
    break_image: BreakImageSettings,
) -> PreparedImageAsset:
    if layer.image_path is None:
        raise ImageAssetError(f"layer {layer.id} has no image")
    suffix = layer.image_path.suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ImageAssetError(f"unsupported image format: {suffix}")

    try:
        with Image.open(layer.image_path) as source:
            source.load()
            rgba = source.convert("RGBA")
    except (OSError, UnidentifiedImageError) as exc:
        raise ImageAssetError(f"failed to load image: {layer.image_path}") from exc

    if rgba.width < break_image.split.columns or rgba.height < break_image.split.rows:
        raise ImageAssetError("break_image.split exceeds source image pixel dimensions")

    if break_image.load_mode == "remove_background":
        rgba = _remove_corner_background(rgba, break_image.background_tolerance)

    active = _active_tiles(
        rgba,
        columns=break_image.split.columns,
        rows=break_image.split.rows,
    )
    return PreparedImageAsset(
        id=layer.id,
        width=rgba.width,
        height=rgba.height,
        rgba=rgba.tobytes(),
        active_tiles=active,
    )
