"""pygame rendering for the current application state."""

import pygame

from breakout_forge.contracts.frame import FrameResult
from breakout_forge.contracts.game_state import GameState
from breakout_forge.contracts.settings import AppearanceSettings


class RenderProcessing:
    """Render process snapshots without owning game-state transitions."""

    def __init__(self, appearance: AppearanceSettings) -> None:
        self._appearance = appearance

    def render(self, screen: pygame.Surface, result: FrameResult) -> None:
        screen.fill(self._appearance.background_rgb)

        gameplay = result.gameplay
        if gameplay is not None:
            scale_x = screen.get_width() / gameplay.playfield_width
            scale_y = screen.get_height() / gameplay.playfield_height

            for block in gameplay.blocks:
                rect = block.rect
                pygame.draw.rect(
                    screen,
                    self._appearance.block_rgb,
                    pygame.Rect(
                        round(rect.x * scale_x),
                        round(rect.y * scale_y),
                        max(1, round(rect.width * scale_x)),
                        max(1, round(rect.height * scale_y)),
                    ),
                )

            paddle = gameplay.paddle
            pygame.draw.rect(
                screen,
                self._appearance.paddle_rgb,
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
                    self._appearance.ball_rgb,
                    pygame.Rect(
                        round(ball.x * scale_x),
                        round(ball.y * scale_y),
                        max(1, round(ball.size * scale_x)),
                        max(1, round(ball.size * scale_y)),
                    ),
                )

            score_font = pygame.font.Font(None, self._appearance.score_font_size)
            score_text = score_font.render(
                f"Score: {gameplay.score}",
                True,
                self._appearance.text_rgb,
            )
            screen.blit(score_text, (12, 10))

        if result.state is not GameState.PLAYING:
            font = pygame.font.Font(None, self._appearance.overlay_font_size)
            label = {
                GameState.READY: "Press Space / Enter to start",
                GameState.CLEAR: "Clear - Press R to restart",
                GameState.GAME_OVER: "Game Over - Press R to restart",
            }.get(result.state)
            if label:
                text = font.render(label, True, self._appearance.text_rgb)
                rect = text.get_rect(center=screen.get_rect().center)
                screen.blit(text, rect)

        pygame.display.flip()
