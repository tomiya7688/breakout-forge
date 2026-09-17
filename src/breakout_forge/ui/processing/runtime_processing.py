"""pygame-specific UI runtime processing."""

from __future__ import annotations

import pygame

from breakout_forge.ui.messenger import UiMessenger


class RuntimeProcessing:
    """Own pygame initialization, event polling, timing and presentation."""

    def __init__(
        self,
        messenger: UiMessenger,
        *,
        width: int = 800,
        height: int = 600,
        fps: int = 60,
        title: str = "Breakout Forge",
    ) -> None:
        self._messenger = messenger
        self._width = width
        self._height = height
        self._fps = fps
        self._title = title

    def run(self) -> int:
        pygame.init()
        try:
            screen = pygame.display.set_mode((self._width, self._height))
            pygame.display.set_caption(self._title)
            clock = pygame.time.Clock()
            running = True

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                delta_seconds = clock.tick(self._fps) / 1000.0
                if running:
                    result = self._messenger.update_frame(delta_seconds)
                    running = result.running

                screen.fill((16, 18, 24))
                pygame.display.flip()

            return 0
        finally:
            pygame.quit()
