from pathlib import Path

from scripts.prepare_dist import prepare_distribution


def test_prepare_distribution_copies_external_dirs_and_creates_userdata(tmp_path: Path) -> None:
    project = tmp_path / "project"
    dist = tmp_path / "dist" / "BreakoutForge"

    for name in ("config", "assets", "stages", "mods"):
        directory = project / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "marker.txt").write_text(name, encoding="utf-8")
    (project / "README.md").write_text("readme", encoding="utf-8")
    (project / "LICENSE").write_text("license", encoding="utf-8")

    prepare_distribution(project, dist)

    for name in ("config", "assets", "stages", "mods"):
        assert (dist / name / "marker.txt").read_text(encoding="utf-8") == name

    assert (dist / "userdata").is_dir()
    assert (dist / "README.md").read_text(encoding="utf-8") == "readme"
    assert (dist / "LICENSE").read_text(encoding="utf-8") == "license"


def test_prepare_distribution_replaces_stale_external_copy(tmp_path: Path) -> None:
    project = tmp_path / "project"
    dist = tmp_path / "dist" / "BreakoutForge"

    for name in ("config", "assets", "stages", "mods"):
        directory = project / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "current.txt").write_text("current", encoding="utf-8")
    (project / "README.md").write_text("readme", encoding="utf-8")
    (project / "LICENSE").write_text("license", encoding="utf-8")

    stale = dist / "config"
    stale.mkdir(parents=True, exist_ok=True)
    (stale / "stale.txt").write_text("stale", encoding="utf-8")

    prepare_distribution(project, dist)

    assert not (dist / "config" / "stale.txt").exists()
    assert (dist / "config" / "current.txt").is_file()
