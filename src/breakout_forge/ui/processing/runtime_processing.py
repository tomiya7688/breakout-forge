"""pygame-specific UI runtime processing."""

from __future__ import annotations

import pygame

from breakout_forge.contracts.image_asset import PreparedImageAsset
from breakout_forge.contracts.settings import AppearanceSettings, DisplaySettings
from breakout_forge.ui.messenger import UiMessenger
from breakout_forge.ui.processing.event_processing import EventProcessing
from breakout_forge.ui.processing.render_processing import RenderProcessing


class RuntimeProcessing:
    """Own the pygame loop while delegating event and render work."""

    def __init__(
        self,
        messenger: UiMessenger,
        display_settings: DisplaySettings,
        appearance_settings: AppearanceSettings,
        prepared_assets: tuple[PreparedImageAsset, ...] = (),
        event_processing: EventProcessing | None = None,
        render_processing: RenderProcessing | None = None,
    ) -> None:
        self._messenger = messenger
        self._display_settings = display_settings
        self._appearance_settings = appearance_settings
        self._event_processing = event_processing or EventProcessing()
        self._render_processing = render_processing or RenderProcessing(
            appearance_settings,
            prepared_assets=prepared_assets,
        )

    def run(self) -> int:
        pygame.init()
        try:
            screen = pygame.display.set_mode(
                (self._display_settings.width, self._display_settings.height)
            )
            pygame.display.set_caption(self._display_settings.title)
            clock = pygame.time.Clock()
            running = True

            while running:
                frame_input = self._event_processing.poll()
                if frame_input.quit_requested:
                    break

                delta_seconds = clock.tick(self._display_settings.fps) / 1000.0
                result = self._messenger.update_frame(
                    delta_seconds,
                    start_requested=frame_input.start_requested,
                    restart_requested=frame_input.restart_requested,
                    move_axis=frame_input.move_axis,
                )
                running = result.running
                self._render_processing.render(screen, result)

            return 0
        finally:
            pygame.quit()
