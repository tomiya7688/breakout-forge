"""Example external MOD for Breakout Forge."""

import logging

logger = logging.getLogger("breakout_forge.mods.example")


def setup(api):
    api.subscribe("on_stage_loaded", on_stage_loaded)
    api.subscribe("on_layer_destroyed", on_layer_destroyed)
    api.subscribe("on_stage_cleared", on_stage_cleared)


def on_stage_loaded(event):
    logger.info("stage loaded: %s", event.data.get("stage_name"))


def on_layer_destroyed(event):
    logger.info(
        "layer destroyed: (%s, %s) %s",
        event.data.get("column"),
        event.data.get("row"),
        event.data.get("layer_id"),
    )


def on_stage_cleared(event):
    logger.info("stage cleared: score=%s", event.data.get("score"))
