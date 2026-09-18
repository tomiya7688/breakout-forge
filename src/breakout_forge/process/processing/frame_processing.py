"""Pure process-layer work for one frame."""

from dataclasses import replace

from breakout_forge.contracts.frame import FrameRequest, FrameResult
from breakout_forge.contracts.game_state import GameState
from breakout_forge.contracts.mod_event import ModEvent, ModEventName
from breakout_forge.modding.api import ModApi
from breakout_forge.process.processing.paddle_ball_processing import PaddleBallProcessing
from breakout_forge.process.processing.stage_runtime import StageRuntime
from breakout_forge.process.processing.state_processing import StateProcessing


class FrameProcessing:
    """Coordinate process-layer work for one frame."""

    def __init__(
        self,
        state_processing: StateProcessing | None = None,
        paddle_ball_processing: PaddleBallProcessing | None = None,
        stage_processing: StageRuntime | None = None,
        mod_api: ModApi | None = None,
    ) -> None:
        self._state_processing = state_processing or StateProcessing()
        self._paddle_ball_processing = paddle_ball_processing
        self._stage_processing = stage_processing
        self._mod_api = mod_api

    @property
    def state_processing(self) -> StateProcessing:
        return self._state_processing

    def emit_stage_loaded(self, stage_id: str, stage_name: str) -> None:
        self._emit(
            ModEventName.STAGE_LOADED,
            {"stage_id": stage_id, "stage_name": stage_name},
        )

    def _emit(self, name: ModEventName, data: dict[str, object]) -> None:
        if self._mod_api is not None:
            self._mod_api.emit(ModEvent(name=name, data=data))

    def _emit_collision_events(self) -> None:
        if self._paddle_ball_processing is None:
            return
        for collision in self._paddle_ball_processing.last_board_collisions:
            damage = collision.damage
            self._emit(
                ModEventName.BLOCK_HIT,
                {
                    "column": collision.column,
                    "row": collision.row,
                    "reflected_x": collision.reflected_x,
                    "reflected_y": collision.reflected_y,
                    "layer_id": damage.target_layer_id if damage else None,
                },
            )
            if damage is None:
                continue
            if damage.layer_destroyed:
                self._emit(
                    ModEventName.LAYER_DESTROYED,
                    {
                        "column": damage.column,
                        "row": damage.row,
                        "layer_id": damage.target_layer_id,
                        "next_layer_id": damage.next_layer_id,
                    },
                )
            if damage.layer_destroyed and damage.cell_empty:
                self._emit(
                    ModEventName.CELL_DESTROYED,
                    {
                        "column": damage.column,
                        "row": damage.row,
                        "layer_id": damage.target_layer_id,
                    },
                )

    def execute(self, request: FrameRequest) -> FrameResult:
        if request.delta_seconds < 0:
            raise ValueError("delta_seconds must be non-negative")

        previous_state = self._state_processing.state
        state = self._state_processing.apply_requests(
            start_requested=request.start_requested,
            restart_requested=request.restart_requested,
        )
        if previous_state is GameState.READY and state is GameState.PLAYING:
            self._emit(ModEventName.GAME_START, {})

        if self._paddle_ball_processing is not None:
            returning_to_ready = (
                request.restart_requested
                or (previous_state is not GameState.READY and state is GameState.READY)
            )
            if returning_to_ready:
                if self._stage_processing is not None:
                    board = self._stage_processing.reset()
                    self._paddle_ball_processing.set_board(board)
                self._paddle_ball_processing.reset()

            if state is GameState.PLAYING:
                all_balls_lost = self._paddle_ball_processing.update(
                    request.delta_seconds,
                    request.move_axis,
                )
                self._emit(
                    ModEventName.GAME_UPDATE,
                    {"delta_seconds": request.delta_seconds},
                )
                for _ in range(self._paddle_ball_processing.last_paddle_hits):
                    self._emit(ModEventName.BALL_HIT_PADDLE, {})
                self._emit_collision_events()

                if self._stage_processing is not None:
                    self._stage_processing.register_collisions(
                        self._paddle_ball_processing.last_board_collisions
                    )
                    if self._stage_processing.cleared:
                        state = self._state_processing.mark_clear()
                        self._emit(
                            ModEventName.STAGE_CLEARED,
                            {"score": self._stage_processing.score},
                        )
                    elif all_balls_lost:
                        state = self._state_processing.mark_game_over()
                        self._emit(
                            ModEventName.GAME_OVER,
                            {"score": self._stage_processing.score},
                        )
                elif all_balls_lost:
                    state = self._state_processing.mark_game_over()
                    self._emit(ModEventName.GAME_OVER, {})

            gameplay = self._paddle_ball_processing.snapshot()
            if self._stage_processing is not None:
                gameplay = replace(
                    gameplay,
                    blocks=self._stage_processing.block_snapshots(),
                    score=self._stage_processing.score,
                )
        else:
            gameplay = None

        return FrameResult(running=True, state=state, gameplay=gameplay)
