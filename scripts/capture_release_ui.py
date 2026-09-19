"""Capture deterministic UI screenshots for formal release review."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from breakout_forge.contracts.frame import FrameResult
from breakout_forge.contracts.game_state import GameState
from breakout_forge.data.commander import DataCommander
from breakout_forge.data.messenger import DataMessenger
from breakout_forge.data.processing.settings_processing import resolve_runtime_settings
from breakout_forge.process.processing.image_stage_processing import ImageStageProcessing
from breakout_forge.process.processing.layer_damage_processing import LayerDamageProcessing
from breakout_forge.process.processing.paddle_ball_processing import PaddleBallProcessing
from breakout_forge.process.processing.standard_stage_processing import StandardStageProcessing
from breakout_forge.ui.processing.render_processing import RenderProcessing


def _standard_snapshot(root: Path):
    settings = resolve_runtime_settings(root / "config" / "common.json")
    stage = StandardStageProcessing(
        settings.stage_size,
        settings.standard_stage,
        settings.playfield,
    )
    paddle_ball = PaddleBallProcessing(
        settings.gameplay,
        settings.playfield,
        board=stage.board,
    )
    gameplay = replace(
        paddle_ball.snapshot(),
        blocks=stage.block_snapshots(),
        score=stage.score,
    )
    return settings, gameplay


def _image_snapshot(root: Path, stage_id: str, *, break_top: bool = False):
    data = DataMessenger(DataCommander())
    stage = data.load_stage(
        root / "config" / "common.json",
        root / "stages" / stage_id / "stage.json",
    )
    layers = tuple(layer for layer in stage.layers if layer.image_path is not None)
    assets = tuple(data.prepare_image(layer, stage.settings.break_image) for layer in layers)
    runtime = ImageStageProcessing(
        stage,
        layers,
        assets,
        stage.settings.playfield,
        stage.settings.standard_stage,
    )

    if break_top:
        cell = next(
            cell for cell in runtime.board.non_empty_cells()
            if len(cell.layers) >= 2
        )
        damage = LayerDamageProcessing()
        while cell.top_visible_layer() is not None and cell.top_visible_layer().asset_id == "top":
            damage.apply(cell)

    paddle_ball = PaddleBallProcessing(
        stage.settings.gameplay,
        stage.settings.playfield,
        board=runtime.board,
    )
    gameplay = replace(
        paddle_ball.snapshot(),
        blocks=runtime.block_snapshots(),
        score=runtime.score,
    )
    return stage.settings, gameplay, assets


def _capture(
    output: Path,
    name: str,
    settings,
    result: FrameResult,
    assets=(),
) -> dict[str, object]:
    screen = pygame.display.set_mode((settings.display.width, settings.display.height))
    renderer = RenderProcessing(settings.appearance, prepared_assets=tuple(assets))
    renderer.render(screen, result)
    path = output / f"{name}.png"
    pygame.image.save(screen, path)
    return {
        "name": name,
        "file": path.name,
        "width": settings.display.width,
        "height": settings.display.height,
        "state": result.state.value,
    }


def capture_release_ui(project_root: Path, output: Path) -> list[dict[str, object]]:
    root = project_root.resolve()
    output.mkdir(parents=True, exist_ok=True)
    screenshots: list[dict[str, object]] = []

    pygame.init()
    try:
        settings, gameplay = _standard_snapshot(root)
        screenshots.append(
            _capture(
                output,
                "01-ready",
                settings,
                FrameResult(state=GameState.READY, gameplay=gameplay),
            )
        )
        screenshots.append(
            _capture(
                output,
                "02-standard-playing",
                settings,
                FrameResult(state=GameState.PLAYING, gameplay=gameplay),
            )
        )
        screenshots.append(
            _capture(
                output,
                "08-clear",
                settings,
                FrameResult(
                    state=GameState.CLEAR,
                    gameplay=replace(gameplay, blocks=()),
                ),
            )
        )
        screenshots.append(
            _capture(
                output,
                "09-game-over",
                settings,
                FrameResult(
                    state=GameState.GAME_OVER,
                    gameplay=replace(gameplay, balls=()),
                ),
            )
        )

        image_settings, image_gameplay, image_assets = _image_snapshot(root, "sample")
        screenshots.append(
            _capture(
                output,
                "03-image-stage",
                image_settings,
                FrameResult(state=GameState.PLAYING, gameplay=image_gameplay),
                image_assets,
            )
        )

        remove_settings, remove_gameplay, remove_assets = _image_snapshot(
            root,
            "remove_background_sample",
        )
        screenshots.append(
            _capture(
                output,
                "04-remove-background",
                remove_settings,
                FrameResult(state=GameState.PLAYING, gameplay=remove_gameplay),
                remove_assets,
            )
        )

        layered_settings, layered_gameplay, layered_assets = _image_snapshot(
            root,
            "layered_sample",
        )
        screenshots.append(
            _capture(
                output,
                "05-layered-top",
                layered_settings,
                FrameResult(state=GameState.PLAYING, gameplay=layered_gameplay),
                layered_assets,
            )
        )

        broken_settings, broken_gameplay, broken_assets = _image_snapshot(
            root,
            "layered_sample",
            break_top=True,
        )
        screenshots.append(
            _capture(
                output,
                "06-layered-revealed",
                broken_settings,
                FrameResult(state=GameState.PLAYING, gameplay=broken_gameplay),
                broken_assets,
            )
        )
    finally:
        pygame.quit()

    manifest = {
        "format_version": 1,
        "screenshots": screenshots,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return screenshots


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    capture_release_ui(args.project_root, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
