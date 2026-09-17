"""Process-layer Paddle/Ball movement and collision work."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from breakout_forge.contracts.gameplay import BallSnapshot, GameplaySnapshot, RectSnapshot
from breakout_forge.contracts.settings import GameplaySettings, PlayfieldSettings
from breakout_forge.process.model.board import Board
from breakout_forge.process.processing.collision import (
    BoardCollisionProcessing,
    BoardCollisionResult,
)


@dataclass(slots=True)
class _Paddle:
    x: float
    y: float
    width: float
    height: float


@dataclass(slots=True)
class _Ball:
    x: float
    y: float
    vx: float
    vy: float
    size: float


class PaddleBallProcessing:
    """Own mutable paddle/ball state without depending on pygame."""

    def __init__(
        self,
        gameplay: GameplaySettings,
        playfield: PlayfieldSettings,
        board: Board | None = None,
        board_collision_processing: BoardCollisionProcessing | None = None,
    ) -> None:
        self._settings = gameplay
        self._playfield = playfield
        self._board = board
        self._board_collision_processing = (
            board_collision_processing or BoardCollisionProcessing()
        )
        self._last_board_collisions: tuple[BoardCollisionResult, ...] = ()
        self._paddle: _Paddle
        self._balls: list[_Ball]
        self.reset()

    @property
    def last_board_collisions(self) -> tuple[BoardCollisionResult, ...]:
        return self._last_board_collisions

    def set_board(self, board: Board | None) -> None:
        """Replace the active board without coupling board creation to this processor."""

        self._board = board
        self._last_board_collisions = ()

    def reset(self) -> None:
        paddle_width = float(self._settings.paddle_size.width)
        paddle_height = float(self._settings.paddle_size.height)
        paddle_x = (self._playfield.width - paddle_width) / 2.0
        paddle_y = (
            self._playfield.height
            - self._settings.paddle_bottom_margin
            - paddle_height
        )
        self._paddle = _Paddle(paddle_x, paddle_y, paddle_width, paddle_height)

        direction = self._settings.ball_initial_direction
        length = hypot(direction.x, direction.y)
        vx = direction.x / length * self._settings.ball_speed
        vy = direction.y / length * self._settings.ball_speed
        size = float(self._settings.ball_size)
        self._balls = [
            _Ball(
                x=(self._playfield.width - size) / 2.0,
                y=paddle_y - size - 4.0,
                vx=vx,
                vy=vy,
                size=size,
            )
        ]
        self._last_board_collisions = ()

    def update(self, delta_seconds: float, move_axis: float) -> bool:
        """Advance gameplay and return True when all balls have fallen out."""
        axis = max(-1.0, min(1.0, move_axis))
        self._paddle.x += axis * self._settings.paddle_speed * delta_seconds
        self._paddle.x = max(
            0.0,
            min(self._paddle.x, self._playfield.width - self._paddle.width),
        )

        survivors: list[_Ball] = []
        collisions: list[BoardCollisionResult] = []
        for ball in self._balls:
            previous_x = ball.x
            previous_y = ball.y
            ball.x += ball.vx * delta_seconds
            ball.y += ball.vy * delta_seconds

            if ball.x < 0.0:
                ball.x = 0.0
                ball.vx = abs(ball.vx)
            elif ball.x + ball.size > self._playfield.width:
                ball.x = self._playfield.width - ball.size
                ball.vx = -abs(ball.vx)

            if ball.y < 0.0:
                ball.y = 0.0
                ball.vy = abs(ball.vy)

            if self._board is not None:
                collision = self._board_collision_processing.resolve(
                    ball,
                    self._board,
                    previous_x=previous_x,
                    previous_y=previous_y,
                )
                if collision.collided:
                    collisions.append(collision)

            if self._intersects_paddle(ball) and ball.vy > 0:
                ball.y = self._paddle.y - ball.size
                ball.vy = -abs(ball.vy)

            if ball.y <= self._playfield.height:
                survivors.append(ball)

        self._balls = survivors
        self._last_board_collisions = tuple(collisions)
        return not self._balls

    def _intersects_paddle(self, ball: _Ball) -> bool:
        return (
            ball.x < self._paddle.x + self._paddle.width
            and ball.x + ball.size > self._paddle.x
            and ball.y < self._paddle.y + self._paddle.height
            and ball.y + ball.size > self._paddle.y
        )

    def snapshot(self) -> GameplaySnapshot:
        return GameplaySnapshot(
            paddle=RectSnapshot(
                x=self._paddle.x,
                y=self._paddle.y,
                width=self._paddle.width,
                height=self._paddle.height,
            ),
            balls=tuple(BallSnapshot(x=b.x, y=b.y, size=b.size) for b in self._balls),
            playfield_width=float(self._playfield.width),
            playfield_height=float(self._playfield.height),
        )
