"""pygame rendering for the current application state."""

import pygame

from breakout_forge.contracts.game_state import GameState


class RenderProcessing:
    """Render the current state without owning game-state transitions."""

    def render(self, screen: pygame.Surface, state: GameState) -> None:
        screen.fill((16, 18, 24))

        font = pygame.font.Font(None, 36)
        label = {
            GameState.READY: "Press Space / Enter to start",
            GameState.PLAYING: "Playing",
            GameState.CLEAR: "Clear - Press R to restart",
            GameState.GAME_OVER: "Game Over - Press R to restart",
        }[state]
        text = font.render(label, True, (230, 230, 230))
        rect = text.get_rect(center=screen.get_rect().center)
        screen.blit(text, rect)
        pygame.display.flip()
