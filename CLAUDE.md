# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Architecture

Password Wizard is a Pygame-based tower defense game where players create "potion passwords" to defend against waves of enemies. The game teaches password security concepts through gameplay mechanics.

### Core Files

- **main.py** - Game loop, state machine, UI rendering, and event handling
- **battle.py** - Enemy sprites (SmallGoblin, Soldier), Arrow projectile, tower rendering, and battle resolution
- **potions.py** - Password power calculation, inventory/shop system, and input handling

### Game State Machine

States flow: `MENU` → `STORY` → `IDLE` ↔ `BATTLE` → `DEFEAT` or `GAME OVER`

- `MENU`: Title screen with play button
- `STORY`: Sequential comic panels (click to advance)
- `IDLE`: Shop and password input phase; tutorial shown on Wave 1
- `BATTLE`: Enemies march toward tower, arrows fire, then battle resolves
- `DEFEAT`/`GAME OVER`: End states (press R to restart)

### Password Power System (potions.py)

Characters have base power values: lowercase=5, uppercase=15, special=25, numbers=35. Using multiple character types applies a chain bonus multiplier (up to 2x for all four types).

Players must purchase inventory (uppercase, special, numbers) from the shop before typing those characters. Lowercase is always free. Password length is limited by: `4 + (wave * 2) + purchased_limit`.

### Battle Resolution (battle.py)

Power is subtracted sequentially from each enemy's power value. If player power runs out before defeating all enemies, the wave is lost. Victory awards coins equal to the sum of enemy values.

### Assets

All sprites and fonts are in `assets/`. The game uses sprite sheets for potions, enemies, towers, and a custom "Daydream.otf" font.