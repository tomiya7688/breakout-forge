"""Transport-friendly results for block-layer damage processing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LayerDamageResult:
    """Describe the outcome of applying one damage operation to a cell."""

    column: int
    row: int
    target_layer_id: str | None
    damage_requested: int
    damage_applied: int
    hp_before: int | None
    hp_after: int | None
    layer_destroyed: bool
    cell_empty: bool
    next_layer_id: str | None
    ignored_reason: str | None = None
