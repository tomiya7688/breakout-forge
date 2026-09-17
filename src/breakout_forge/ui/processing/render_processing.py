"""pygame rendering for the current application state."""

import pygame

from breakout_forge.contracts.frame import FrameResult
from breakout_forge.contracts.game_state import GameState


class RenderProcessing:
    """Render process snapshots without owning game-state transitions."""

    def render(self, screen: pygame.Surface, result: FrameResult) -> None:
        screen.fill((16, 18, 24))

        gameplay = result.gameplay
        if gameplay is not None:
            scale_x = screen.get_width() / gameplay.playfield_width
            scale_y = screen.get_height() / gameplay.playfield_height
            paddle = gameplay.paddle
            pygame.draw.rect(
                screen,
                (230, 230, 230),
                pygame.Rect(
                    round(paddle.x * scale_x),
                    round(paddle.y * scale_y),
                    max(1, round(paddle.width * scale_x)),
                    max(1, round(paddle.height * scale_y)),
                ),
            )
            for ball in gameplay.balls:
                pygame.draw.ellipse(
                    screen,
                    (230, 230, 230),
                    pygame.Rect(
                        round(ball.x * scale_x),
                        round(ball.y * scale_y),
                        max(1, round(ball.size * scale_x)),
                        max(1, round(ball.size * scale_y)),
                    ),
                )

        if result.state is not GameState.PLAYING:
            font = pygame.font.Font(None, 36)
            label = {
                GameState.READY: "Press Space / Enter to start",
                GameState.CLEAR: "Clear - Press R to restart",
                GameState.GAME_OVER: "Game Over - Press R to restart",
            }.get(result.state)
            if label:
                text = font.render(label, True, (230, 230, 230))
                rect = text.get_rect(center=screen.get_rect().center)
                screen.blit(text, rect)

        pygame.display.flip()
