import pytest

from breakout_forge.process.model.board import BlockCell, BlockLayer, RectValue
from breakout_forge.process.processing.layer_damage_processing import LayerDamageProcessing


def _cell(*layers: BlockLayer) -> BlockCell:
    return BlockCell(
        column=2,
        row=3,
        rect=RectValue(x=0, y=0, width=10, height=10),
        layers=list(layers),
    )


def test_hp_two_layer_requires_two_hits() -> None:
    cell = _cell(BlockLayer(id="armor", hp=2, max_hp=2))
    processing = LayerDamageProcessing()

    first = processing.apply(cell)
    second = processing.apply(cell)

    assert first.hp_before == 2
    assert first.hp_after == 1
    assert first.layer_destroyed is False
    assert second.hp_before == 1
    assert second.hp_after == 0
    assert second.layer_destroyed is True
    assert cell.empty is True


def test_destroying_top_layer_exposes_lower_layer() -> None:
    cell = _cell(
        BlockLayer(id="background"),
        BlockLayer(id="main"),
        BlockLayer(id="armor"),
    )
    processing = LayerDamageProcessing()

    result = processing.apply(cell)

    assert result.target_layer_id == "armor"
    assert result.layer_destroyed is True
    assert result.next_layer_id == "main"
    assert cell.top_layer().id == "main"


def test_destroying_last_layer_makes_cell_empty() -> None:
    cell = _cell(BlockLayer(id="only"))

    result = LayerDamageProcessing().apply(cell)

    assert result.cell_empty is True
    assert result.next_layer_id is None
    assert cell.empty is True


def test_indestructible_top_layer_blocks_damage_to_lower_layers() -> None:
    lower = BlockLayer(id="lower", hp=1, max_hp=1)
    shield = BlockLayer(id="shield", hp=1, max_hp=1, destructible=False)
    cell = _cell(lower, shield)

    result = LayerDamageProcessing().apply(cell, damage=5)

    assert result.ignored_reason == "indestructible"
    assert result.damage_applied == 0
    assert shield.hp == 1
    assert lower.hp == 1
    assert result.next_layer_id == "shield"


def test_non_collidable_top_layer_does_not_hide_collidable_target() -> None:
    target = BlockLayer(id="target", hp=1, max_hp=1)
    decoration = BlockLayer(id="decoration", collidable=False, destructible=False)
    cell = _cell(target, decoration)

    result = LayerDamageProcessing().apply(cell)

    assert result.target_layer_id == "target"
    assert result.layer_destroyed is True
    assert cell.top_layer().id == "decoration"
    assert result.cell_empty is False
    assert result.next_layer_id is None


def test_excess_damage_does_not_spill_into_next_layer() -> None:
    lower = BlockLayer(id="lower", hp=3, max_hp=3)
    upper = BlockLayer(id="upper", hp=1, max_hp=1)
    cell = _cell(lower, upper)

    result = LayerDamageProcessing().apply(cell, damage=99)

    assert result.damage_applied == 1
    assert upper.hp == 0
    assert lower.hp == 3
    assert result.next_layer_id == "lower"


def test_empty_or_non_collidable_cell_returns_ignored_result() -> None:
    cell = _cell(BlockLayer(id="background", collidable=False))

    result = LayerDamageProcessing().apply(cell)

    assert result.target_layer_id is None
    assert result.damage_applied == 0
    assert result.ignored_reason == "no_collidable_layer"
    assert result.cell_empty is False


@pytest.mark.parametrize("damage", [0, -1, 1.5, True])
def test_damage_must_be_positive_integer(damage: object) -> None:
    cell = _cell(BlockLayer(id="target"))

    with pytest.raises(ValueError):
        LayerDamageProcessing().apply(cell, damage)  # type: ignore[arg-type]
