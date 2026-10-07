# Rhythm Tap

A 4-lane rhythm game built with Pygame — tap and hold the right keys as notes reach the hit line.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action / Lane |
|-----|---------------|
| D | Lane 1 (Red) — Tap or Hold |
| F | Lane 2 (Cyan) — Tap or Hold |
| J | Lane 3 (Green) — Tap or Hold |
| K | Lane 4 (Yellow) — Tap or Hold |
| R | Restart game |

## Features & Improvements

### Tunable Constants (`game/game_engine.py`)
- `BPM = 120`: Sets tempo (120 BPM = 0.5s per beat).
- `HOLD_DURATION = 1.0`: Duration (in seconds) that hold notes must be held.
- `HOLD_PROBABILITY = 0.2`: Proportion (~20% or 1 in 5) of spawned notes that are hold notes.
- `HOLD_GAP = 60`: Minimum clearance gap (in pixels) required behind a hold note before a new note can spawn in the same lane.
- `INITIAL_SPEED = 5.0`, `MAX_SPEED = 10.0`, `SPEED_INCREMENT = 0.5`: Controls falling note speed.
- `DIFFICULTY_RAMP_INTERVAL = 10.0`: Gradually and reliably increases scroll speed every 10 seconds of play.
- `MAX_MISSES = 15`: Maximum allowed misses before game over.

---

### Step 0: Difficulty Ramping & MISS Consistency Bug Fixes
- **Steady Difficulty Ramp**: Decoupled difficulty progression from frame-modulo spawns. Note speed now ramps up reliably every 10 seconds of gameplay.
- **Accurate MISS Counter & Popups**: Stray or mistimed key presses now only reset the active combo without producing a false "MISS" popup or incrementing the miss counter.
- **Immediate Miss Detection**: Notes are marked as missed and display the red "MISS" popup immediately upon crossing past the lower edge of the hit window.

### Task 1: Synthesized Sound Effects on Hit
- Procedurally synthesized pure sine-wave tones generated at runtime via Python's standard library (`math`, `wave`, `struct`, `io`) and loaded into `pygame.mixer.Sound`.
- Distinct pitch grading:
  - **PERFECT**: 880 Hz (A5)
  - **GREAT**: 660 Hz (E5)
  - **OK**: 520 Hz (C5)
- Includes defensive error handling so the game runs smoothly even on systems without an active audio device.

### Task 2: Hold Notes
- Hold notes spawn approximately 1 in 5 notes (`HOLD_PROBABILITY = 0.2`) with height corresponding to 1 second of travel distance at current speed.
- **Collision Avoidance**: Spawning checks lane occupancy to ensure new notes are never placed in a lane currently occupied by a falling hold bar (including a `HOLD_GAP` safety margin); blocked lanes are automatically rerouted to free lanes.
- Tapping the head registers the accuracy grade and activates a visual brightness highlight while held.
- Holding the key until the tail reaches the hit line awards score and combo based on initial hit accuracy.
- Releasing the key early (`pygame.KEYUP`) triggers a MISS and resets the combo.

### Task 3: BPM-Synced Spawning
- Replaced the frame-counter spawn interval with an elapsed-time beat clock driven by the `BPM = 120` constant (0.5 seconds per beat).
- Automatically calculates fall time based on current fall speed (`t_fall = fall_distance / speed_pps`) and spawns notes ahead of time so they arrive at the hit line exactly on the beat.
- Seamlessly adjusts to difficulty speed ramps and cleanly resets on pressing `R`.

### Task 4: Grade Summary Screen
- Tracks exact performance statistics during the game: `PERFECT`, `GREAT`, `OK`, and `MISS`.
- Upon game over, displays a breakdown:
  - Counts for PERFECT, GREAT, OK, and MISS
  - Accuracy percentage: `(hits / total_judged) * 100`, formatted to 1 decimal place (e.g., `85.4%`)
  - Final Score & Max Combo
  - "Press R to Restart" prompt which resets all counters and state cleanly.

## Folder Structure

```
rhythm-tap/
├── main.py
├── requirements.txt
├── game/
│   ├── __init__.py
│   ├── game_engine.py
│   └── beat.py
└── README.md
```

## Submission Checklist

- [ ] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [ ] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [ ] The Chat/LLM used page link, with the complete chat history
