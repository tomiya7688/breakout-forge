"""pygame event polling and UI input translation."""

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class UiFrameInput:
    quit_requested: bool = False
    start_requested: bool = False
    restart_requested: bool = False
    move_axis: float = 0.0


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

        keys = pygame.key.get_pressed()
        left = bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
        right = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
        move_axis = float(right) - float(left)

        return UiFrameInput(
            quit_requested=quit_requested,
            start_requested=start_requested,
            restart_requested=restart_requested,
            move_axis=move_axis,
        )
