"""Pure process-layer damage handling for stacked block layers."""

from __future__ import annotations

from breakout_forge.contracts.layer_damage import LayerDamageResult
from breakout_forge.process.model.board import BlockCell


class LayerDamageProcessing:
    """Apply damage to the top collidable layer of a cell.

    Destroyed layers remain in the stack with hp=0 so event consumers and
    debugging tools can still inspect historical layer data. One damage
    operation never spills excess damage into the next layer.
    """

    def apply(self, cell: BlockCell, damage: int = 1) -> LayerDamageResult:
        if isinstance(damage, bool) or not isinstance(damage, int) or damage <= 0:
            raise ValueError("damage must be a positive integer")

        target = cell.top_collidable_layer()
        if target is None:
            return LayerDamageResult(
                column=cell.column,
                row=cell.row,
                target_layer_id=None,
                damage_requested=damage,
                damage_applied=0,
                hp_before=None,
                hp_after=None,
                layer_destroyed=False,
                cell_empty=cell.empty,
                next_layer_id=(cell.top_layer().id if cell.top_layer() else None),
                ignored_reason="no_collidable_layer",
            )

        hp_before = target.hp
        if not target.destructible:
            return LayerDamageResult(
                column=cell.column,
                row=cell.row,
                target_layer_id=target.id,
                damage_requested=damage,
                damage_applied=0,
                hp_before=hp_before,
                hp_after=target.hp,
                layer_destroyed=False,
                cell_empty=cell.empty,
                next_layer_id=target.id,
                ignored_reason="indestructible",
            )

        applied = min(damage, target.hp)
        target.hp -= applied
        destroyed = not target.alive
        next_layer = cell.top_collidable_layer()

        return LayerDamageResult(
            column=cell.column,
            row=cell.row,
            target_layer_id=target.id,
            damage_requested=damage,
            damage_applied=applied,
            hp_before=hp_before,
            hp_after=target.hp,
            layer_destroyed=destroyed,
            cell_empty=cell.empty,
            next_layer_id=next_layer.id if next_layer else None,
            ignored_reason=None,
        )
