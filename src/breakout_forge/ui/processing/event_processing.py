"""pygame event polling and UI input translation."""

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class UiFrameInput:
    quit_requested: bool = False
    start_requested: bool = False
    restart_requested: bool = False


class EventProcessing:
    """Translate pygame events into framework-neutral frame requests."""

    def poll(self) -> UiFrameInput:
        quit_requested = False
        start_requested = False
        restart_requested = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_requested = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    start_requested = True
                elif event.key == pygame.K_r:
                    restart_requested = True

        return UiFrameInput(
            quit_requested=quit_requested,
            start_requested=start_requested,
            restart_requested=restart_requested,
        )
