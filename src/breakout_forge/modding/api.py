"""Public MOD API exposed to external Python modules."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from breakout_forge.contracts.mod_event import ModEvent, ModEventName

ModHandler = Callable[[ModEvent], None]


@dataclass(frozen=True, slots=True)
class _Subscription:
    mod_id: str
    handler: ModHandler


class ModApi:
    """Small event-subscription API for external MODs."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("breakout_forge.mods")
        self._subscriptions: dict[ModEventName, list[_Subscription]] = {
            event_name: [] for event_name in ModEventName
        }
        self._current_mod_id: str | None = None

    def _enter_registration(self, mod_id: str) -> None:
        self._current_mod_id = mod_id

    def _leave_registration(self) -> None:
        self._current_mod_id = None

    def subscribe(self, event_name: str | ModEventName, handler: ModHandler) -> None:
        if self._current_mod_id is None:
            raise RuntimeError("subscribe() is only available while a MOD is registering")
        try:
            name = ModEventName(event_name)
        except ValueError as exc:
            raise ValueError(f"unsupported MOD event: {event_name}") from exc
        if not callable(handler):
            raise TypeError("MOD event handler must be callable")
        self._subscriptions[name].append(
            _Subscription(mod_id=self._current_mod_id, handler=handler)
        )

    def emit(self, event: ModEvent) -> None:
        for subscription in tuple(self._subscriptions[event.name]):
            try:
                subscription.handler(event)
            except Exception:
                self._logger.exception(
                    "MOD event handler failed: mod=%s event=%s",
                    subscription.mod_id,
                    event.name.value,
                )
