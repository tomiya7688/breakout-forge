from pathlib import Path

from breakout_forge.contracts.mod_event import ModEvent, ModEventName
from breakout_forge.data.processing.mod_processing import (
    load_and_register_mods,
    load_mod_definition,
)
from breakout_forge.modding.api import ModApi


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_mod_manifest_and_entry_are_loaded(tmp_path: Path) -> None:
    manifest = _write(
        tmp_path / "mods" / "one" / "mod.json",
        '{"format_version":1,"id":"one","name":"One","version":"1.0","entry":"main.py"}',
    )
    _write(manifest.parent / "main.py", "def setup(api):\n    pass\n")

    definition = load_mod_definition(manifest)

    assert definition.id == "one"
    assert definition.entry_path == (manifest.parent / "main.py").resolve()


def test_mod_can_subscribe_to_multiple_events(tmp_path: Path) -> None:
    mod_dir = tmp_path / "mods" / "one"
    _write(
        mod_dir / "mod.json",
        '{"format_version":1,"id":"one","name":"One","version":"1.0","entry":"main.py"}',
    )
    _write(
        mod_dir / "main.py",
        "events=[]\n"
        "def setup(api):\n"
        "    api.subscribe('on_game_start', lambda event: events.append(event.name.value))\n"
        "    api.subscribe('on_layer_destroyed', lambda event: events.append(event.name.value))\n",
    )
    api = ModApi()

    loaded = load_and_register_mods(tmp_path / "mods", api)
    assert [item.id for item in loaded] == ["one"]

    api.emit(ModEvent(ModEventName.GAME_START, {}))
    api.emit(ModEvent(ModEventName.LAYER_DESTROYED, {"layer_id": "x"}))


def test_handler_exception_does_not_stop_other_mod_handlers() -> None:
    received: list[str] = []
    api = ModApi()

    api._enter_registration("bad")
    api.subscribe("on_game_start", lambda event: (_ for _ in ()).throw(RuntimeError("boom")))
    api._leave_registration()

    api._enter_registration("good")
    api.subscribe("on_game_start", lambda event: received.append(event.name.value))
    api._leave_registration()

    api.emit(ModEvent(ModEventName.GAME_START, {}))

    assert received == ["on_game_start"]


def test_entry_cannot_escape_mod_directory(tmp_path: Path) -> None:
    manifest = _write(
        tmp_path / "mods" / "one" / "mod.json",
        '{"format_version":1,"id":"one","name":"One","version":"1.0","entry":"../outside.py"}',
    )
    _write(manifest.parent.parent / "outside.py", "def setup(api):\n    pass\n")

    try:
        load_mod_definition(manifest)
    except ValueError as exc:
        assert "inside the MOD directory" in str(exc)
    else:
        raise AssertionError("entry path escape must be rejected")
