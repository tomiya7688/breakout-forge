# Breakout Forge Architecture

Breakout Forge applies the principles of UPD Commander Base Design to the game foundation.

## Layers

```text
UI
  Commander -> UI Processing
       |
       v
  UI Messenger
       |
       v
Process Messenger -> Process Commander -> Process Processing
       |
       v (when persistent/external data is required)
Data Messenger -> Data Commander -> Data Processing
```

### UI
Owns pygame-facing input, rendering, window lifecycle and presentation. UI never loads stage/config/mod files directly.

### Process
Owns game rules, simulation, state transitions, collision decisions and stage behavior. Process does not know pygame rendering details or storage formats.

### Data
Owns filesystem access, JSON/config/stage/mod loading, path resolution and persistence. Data does not contain game rules and does not know UI.

### Contracts
`contracts/` contains small transport-only values used at boundaries. Framework-specific objects should not cross boundaries unless a documented exception is required.

## Commander Rule
A Commander performs orchestration only. If a method starts calculating game state, parsing JSON, drawing, converting images or performing filesystem operations, that work belongs in a Processing unit.

## Messenger Rule
A Messenger performs cross-layer communication only. It may package/forward a contract and route a response; it must not implement game/data/rendering logic.

## Processing Rule
Processing modules perform actual work and remain scoped to their layer. Large processing units should be split by responsibility rather than moved into a Commander.

## Composition Root
`breakout_forge.app.create_application()` is the composition root. It wires concrete components together and does not perform runtime game work.

## Current Foundation
The first implementation intentionally contains only a UI runtime loop and a process-frame placeholder. Ball, paddle, board, stage loading and modding are added by later Issues without changing the layer rules above.

## AI Navigation
Use `AI_CONTEXT.md` as the compact entry point. `DESIGN.md` remains the product/feature source of truth; this document is the architecture source of truth for UPD layer placement.
