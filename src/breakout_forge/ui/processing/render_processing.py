"""pygame rendering for the current application state."""

from __future__ import annotations

import pygame

from breakout_forge.contracts.frame import FrameResult
from breakout_forge.contracts.game_state import GameState
from breakout_forge.contracts.image_asset import PreparedImageAsset
from breakout_forge.contracts.settings import AppearanceSettings


class RenderProcessing:
    """Render process snapshots without owning game-state transitions."""

    def __init__(
        self,
        appearance: AppearanceSettings,
        prepared_assets: tuple[PreparedImageAsset, ...] = (),
    ) -> None:
        self._appearance = appearance
        self._assets = {asset.id: asset for asset in prepared_assets}
        self._surfaces: dict[str, pygame.Surface] = {}
        self._tile_cache: dict[
            tuple[str, int, int, int, int, int, int],
            pygame.Surface,
        ] = {}

    def _surface_for(self, asset_id: str) -> pygame.Surface:
        cached = self._surfaces.get(asset_id)
        if cached is not None:
            return cached
        asset = self._assets[asset_id]
        surface = pygame.image.frombytes(
            asset.rgba,
            (asset.width, asset.height),
            "RGBA",
        ).convert_alpha()
        self._surfaces[asset_id] = surface
        return surface

    def _image_tile(
        self,
        asset_id: str,
        source_rect: pygame.Rect,
        width: int,
        height: int,
    ) -> pygame.Surface:
        key = (
            asset_id,
            source_rect.x,
            source_rect.y,
            source_rect.width,
            source_rect.height,
            width,
            height,
        )
        cached = self._tile_cache.get(key)
        if cached is not None:
            return cached

        source = self._surface_for(asset_id)
        tile = source.subsurface(source_rect).copy()
        if tile.get_width() != width or tile.get_height() != height:
            tile = pygame.transform.smoothscale(tile, (width, height))
        self._tile_cache[key] = tile
        return tile

    @staticmethod
    def _scaled_rect(
        x: float,
        y: float,
        width: float,
        height: float,
        scale_x: float,
        scale_y: float,
    ) -> pygame.Rect:
        left = round(x * scale_x)
        top = round(y * scale_y)
        right = round((x + width) * scale_x)
        bottom = round((y + height) * scale_y)
        return pygame.Rect(
            left,
            top,
            max(1, right - left),
            max(1, bottom - top),
        )

    def render(self, screen: pygame.Surface, result: FrameResult) -> None:
        screen.fill(self._appearance.background_rgb)

        gameplay = result.gameplay
        if gameplay is not None:
            scale_x = screen.get_width() / gameplay.playfield_width
            scale_y = screen.get_height() / gameplay.playfield_height

            for block in gameplay.blocks:
                rect = block.rect
                dest = self._scaled_rect(
                    rect.x,
                    rect.y,
                    rect.width,
                    rect.height,
                    scale_x,
                    scale_y,
                )
                if (
                    block.asset_id is not None
                    and block.source_rect is not None
                    and block.asset_id in self._assets
                ):
                    source = block.source_rect
                    tile = self._image_tile(
                        block.asset_id,
                        pygame.Rect(
                            source.x,
                            source.y,
                            source.width,
                            source.height,
                        ),
                        dest.width,
                        dest.height,
                    )
                    screen.blit(tile, dest)
                else:
                    pygame.draw.rect(screen, self._appearance.block_rgb, dest)

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
                rect = text.get_rect(
                    center=(
                        screen.get_rect().centerx,
                        round(screen.get_height() * self._appearance.overlay_center_y_ratio),
                    )
                )
                screen.blit(text, rect)

        pygame.display.flip()
