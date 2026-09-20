from pathlib import Path

from PIL import Image
import pytest

from breakout_forge.contracts.settings import BreakImageSettings, GridSettings
from breakout_forge.contracts.stage import StageLayerDefinition
from breakout_forge.data.processing.image_processing import (
    ImageAssetError,
    prepare_image_asset,
)


def _layer(path: Path) -> StageLayerDefinition:
    return StageLayerDefinition(
        id="main",
        image_path=path,
        hp=1,
        collidable=True,
        destructible=True,
        visible=True,
    )


@pytest.mark.parametrize(
    ("suffix", "format_name"),
    [(".png", "PNG"), (".jpg", "JPEG"), (".webp", "WEBP")],
)
def test_supported_image_formats_are_decoded(
    tmp_path: Path,
    suffix: str,
    format_name: str,
) -> None:
    path = tmp_path / f"source{suffix}"
    Image.new("RGB", (8, 4), (120, 80, 40)).save(path, format=format_name)

    asset = prepare_image_asset(
        _layer(path),
        BreakImageSettings(
            split=GridSettings(columns=2, rows=1),
            load_mode="keep_background",
            background_tolerance=16,
        ),
    )

    assert (asset.width, asset.height) == (8, 4)
    assert asset.active_tiles == frozenset({(0, 0), (1, 0)})
    assert len(asset.rgba) == 8 * 4 * 4


def test_remove_background_makes_background_only_tiles_inactive(tmp_path: Path) -> None:
    path = tmp_path / "subject.png"
    image = Image.new("RGB", (8, 4), (255, 255, 255))
    for y in range(1, 3):
        for x in range(5, 7):
            image.putpixel((x, y), (220, 20, 20))
    image.save(path)

    asset = prepare_image_asset(
        _layer(path),
        BreakImageSettings(
            split=GridSettings(columns=2, rows=1),
            load_mode="remove_background",
            background_tolerance=8,
        ),
    )

    assert asset.active_tiles == frozenset({(1, 0)})


def test_keep_background_keeps_background_tiles_active(tmp_path: Path) -> None:
    path = tmp_path / "subject.png"
    Image.new("RGB", (8, 4), (255, 255, 255)).save(path)

    asset = prepare_image_asset(
        _layer(path),
        BreakImageSettings(
            split=GridSettings(columns=2, rows=1),
            load_mode="keep_background",
            background_tolerance=8,
        ),
    )

    assert asset.active_tiles == frozenset({(0, 0), (1, 0)})


def test_split_cannot_exceed_source_pixel_dimensions(tmp_path: Path) -> None:
    path = tmp_path / "tiny.png"
    Image.new("RGB", (2, 2), (0, 0, 0)).save(path)

    with pytest.raises(ImageAssetError, match="split"):
        prepare_image_asset(
            _layer(path),
            BreakImageSettings(
                split=GridSettings(columns=3, rows=2),
                load_mode="keep_background",
                background_tolerance=0,
            ),
        )
