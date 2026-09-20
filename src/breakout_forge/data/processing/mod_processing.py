"""Discover, validate, load, and register external Python MODs."""

from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

from breakout_forge.contracts.mod import ModDefinition
from breakout_forge.modding.api import ModApi


class ModLoadError(ValueError):
    """Raised when one MOD manifest or entry is invalid."""


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModLoadError(f"failed to read MOD manifest: {path}") from exc
    if not isinstance(raw, dict):
        raise ModLoadError("MOD manifest root must be an object")
    if raw.get("format_version") != 1:
        raise ModLoadError("unsupported MOD format_version")
    return raw


def _required_string(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ModLoadError(f"mod.{key} must be a non-empty string")
    return value


def load_mod_definition(manifest_path: Path) -> ModDefinition:
    raw = _read_manifest(manifest_path)
    mod_dir = manifest_path.parent.resolve()
    entry_name = _required_string(raw, "entry")
    entry_path = (mod_dir / entry_name).resolve()
    try:
        entry_path.relative_to(mod_dir)
    except ValueError as exc:
        raise ModLoadError("mod.entry must remain inside the MOD directory") from exc
    if entry_path.suffix.lower() != ".py":
        raise ModLoadError("mod.entry must point to a .py file")
    if not entry_path.is_file():
        raise ModLoadError(f"MOD entry file not found: {entry_path}")

    return ModDefinition(
        id=_required_string(raw, "id"),
        name=_required_string(raw, "name"),
        version=_required_string(raw, "version"),
        directory=mod_dir,
        entry_path=entry_path,
    )


def discover_mods(mods_dir: Path) -> tuple[ModDefinition, ...]:
    if not mods_dir.exists():
        return ()
    if not mods_dir.is_dir():
        raise ModLoadError(f"MOD path is not a directory: {mods_dir}")

    definitions: list[ModDefinition] = []
    seen_ids: set[str] = set()
    for manifest in sorted(mods_dir.glob("*/mod.json")):
        definition = load_mod_definition(manifest)
        if definition.id in seen_ids:
            raise ModLoadError(f"duplicate MOD id: {definition.id}")
        seen_ids.add(definition.id)
        definitions.append(definition)
    return tuple(definitions)


def _import_mod(definition: ModDefinition) -> ModuleType:
    module_name = f"breakout_forge_external_mod_{definition.id}"
    spec = importlib.util.spec_from_file_location(module_name, definition.entry_path)
    if spec is None or spec.loader is None:
        raise ModLoadError(f"cannot create module spec for MOD: {definition.id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def register_mod(
    definition: ModDefinition,
    api: ModApi,
) -> None:
    module = _import_mod(definition)
    setup = getattr(module, "setup", None)
    if not callable(setup):
        raise ModLoadError(f"MOD {definition.id} must define callable setup(api)")
    api._enter_registration(definition.id)
    try:
        setup(api)
    finally:
        api._leave_registration()


def load_and_register_mods(
    mods_dir: Path,
    api: ModApi,
    logger: logging.Logger | None = None,
) -> tuple[ModDefinition, ...]:
    log = logger or logging.getLogger("breakout_forge.mods")
    if not mods_dir.exists():
        return ()

    loaded: list[ModDefinition] = []
    seen_ids: set[str] = set()
    for manifest in sorted(mods_dir.glob("*/mod.json")):
        try:
            definition = load_mod_definition(manifest)
            if definition.id in seen_ids:
                raise ModLoadError(f"duplicate MOD id: {definition.id}")
            register_mod(definition, api)
            seen_ids.add(definition.id)
            loaded.append(definition)
            log.info(
                "MOD loaded: id=%s name=%s version=%s",
                definition.id,
                definition.name,
                definition.version,
            )
        except Exception:
            log.exception("MOD load failed: %s", manifest)
    return tuple(loaded)
