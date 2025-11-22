# Pokémon Battle - Retro Edition

A fully functional Pokémon battle game built with **pygame**, featuring a retro Game Boy-inspired design with 2-player AI battles. Select your Pokémon and battle against a random opponent!

## 🎮 Features

✨ **6 Unique Pokémon** with distinct stats and move sets:
- **Charizard** (Fire-type) - High attack, balanced stats
- **Blastoise** (Water-type) - High defense, good for tanking
- **Venusaur** (Grass-type) - Balanced attacker
- **Pikachu** (Electric-type) - Fast and agile
- **Gengar** (Ghost-type) - High speed, offensive
- **Alakazam** (Psychic-type) - Highest speed, strong attacker

⚔️ **Dynamic Battle System**:
- Type effectiveness multipliers (Water beats Fire, Fire beats Grass, etc.)
- Balanced damage calculation preventing one-shot kills
- Smart enemy AI that chooses the most effective move
- Real-time battle animations with sprite bobbing and hit shake effects
- Battles typically last 3-5 turns for engaging gameplay

🎨 **Retro Game Boy-Inspired UI**:
- Classic Game Boy green color palette (#9BBC0F)
- Pixel-style fonts (Courier Bold) for authentic retro feel
- Thick black borders on all UI elements
- Clean battle arena with organized info boxes
- Smooth idle animations on Pokémon sprites

🎭 **Custom Sprite Graphics**:
- Unique hand-drawn geometric sprites for each Pokémon
- Color-coded designs matching Pokémon types
- Detailed sprite features (wings, flowers, ears, etc.)

🔊 **Sound Effects** (optional):
- Hit sounds, select sounds, faint sounds
- Background music support (place `.wav` and `.mp3` files in `sounds/` folder)

## 📋 Installation

### Requirements
- Python 3.8+
- pygame 2.6+

### Setup

1. **Clone or navigate to the project directory**
```bash
cd Pokemon\ Game
```

2. **Create and activate a virtual environment** (recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install pygame
```

4. **Run the game**
```bash
python main.py
```

## 🎮 How to Play

### Selection Screen
1. Click on a Pokémon sprite to select it
2. A random opponent is automatically selected
3. Battle begins!

### Battle Screen
1. **Choose your move** by clicking one of the 4 move buttons
2. Your Pokémon attacks first, then opponent counterattacks
3. Watch HP bars decrease with each hit
4. Battle continues until one Pokémon faints

### Game Over
- **Victory:** Opponent's HP reaches 0 → "You win!"
- **Defeat:** Your Pokémon's HP reaches 0 → "You lost..."
- Press **R** to restart with a new Pokémon
- Press **ESC** to quit

## ⚙️ Game Mechanics

### Type Effectiveness Chart
```
Water  → beats → Fire    (2.0x damage)
Fire   → beats → Grass   (2.0x damage)
Grass  → beats → Water   (2.0x damage)
Electric → beats → Water (2.0x damage)

Reverse matchups deal 0.5x damage
All other matchups deal 1.0x damage
```

### Damage Formula
```
Base = Move Power × 0.4 + Attacker Attack × 0.3 - Defender Defense × 0.4
STAB = 1.15× if move type matches Pokémon type, else 1.0×
Type Multiplier = Based on type effectiveness
Random = 0.9-1.0 for variation

Final Damage = Base × STAB × Type Multiplier × Random
(Minimum 1 damage per hit)
```

### Enemy AI
The opponent chooses moves strategically by:
1. Calculating damage for each available move
2. Factoring in type effectiveness against your Pokémon
3. Selecting the move with the highest expected damage

## 📁 File Structure

```
Pokemon Game/
├── main.py                # Main game file (598 lines)
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── assets/                # Pokémon sprite images
│   ├── charizard.png
│   ├── blastoise.png
│   ├── venusaur.png
│   ├── pikachu.png
│   ├── gengar.png
│   └── alakazam.png
└── sounds/                # Optional audio files
    ├── hit.wav
    ├── select.wav
    ├── faint.wav
    └── bgm.mp3
```

## 🎨 UI Position Adjustments

All UI positions can be easily customized. Refer to the position guide at the top of `main.py` (lines 18-28) for an overview of all layout positions.

### Common Position Values to Adjust

**Enemy Pokémon Sprite:**
- `enemy_x = 550` - LEFT/RIGHT position
- `enemy_y = 220` - UP/DOWN position

**Player Pokémon Sprite:**
- `player_x = 150` - LEFT/RIGHT position
- `player_y = 145` - UP/DOWN position

**Attack Buttons:**
- `mb_start_y = 520` - Move buttons vertical position

**Message Box:**
- Y position: `420` - Adjust to move up/down

**Win Screen Text:**
- Y positions: `570` and `630` - Adjust to move up/down

See comments in `main.py` for more customization options!

## 🔧 Customization

### Add New Pokémon

Edit the `create_pokemons()` function in `main.py`:

```python
# Create a new move
thunder_punch = Move("Thunder Punch", 75, "ELECTRIC")

# Create a new Pokémon
raichu = Pokemon(
    "Raichu", "ELECTRIC", 200, 90, 85, 100,
    [thunder_punch, thunderbolt, volt_tackle, quick_attack],
    sprite_name="raichu"
)

# Add sprite image to assets/raichu.png
return [charizard, blastoise, venusaur, pikachu, gengar, alakazam, raichu]
```

### Add New Moves

```python
new_move = Move("Move Name", power_value, "TYPE")
```

**Available Types:** `"FIRE"`, `"WATER"`, `"GRASS"`, `"ELECTRIC"`, `"GHOST"`, `"PSYCHIC"`

### Adjust Game Balance

Modify values in `main.py`:

**Pokémon Stats (around line 220-260):**
```python
Pokemon(name, type, max_hp, attack, defense, speed, moves, sprite_name)
```

**Move Power:**
```python
Move("Move Name", power, "TYPE")  # Adjust power value
```

**Damage Formula (line 155):**
```python
base = move.power * 0.4 + attacker.attack * 0.3 - defender.defense * 0.4
```
- Increase multipliers for more damage
- Decrease for less damage

### Change UI Colors

Edit the color constants at the top of `main.py`:
```python
RETRO_BG = (155, 188, 15)      # Background color
RETRO_DARK = (81, 108, 32)     # Dark border color
RETRO_LIGHT = (188, 220, 72)   # Light UI color
```

## 📝 Add Sound Effects

Place audio files in the `sounds/` folder:
- `hit.wav` - Play when Pokémon takes damage
- `select.wav` - Play when selecting moves/Pokémon
- `faint.wav` - Play when Pokémon faints
- `bgm.mp3` - Background music during battles

(If files don't exist, the game runs fine without them)

## 🎮 Controls

| Key | Action |
|-----|--------|
| **Mouse Click** | Select Pokémon or move |
| **R** | Restart game |
| **ESC** | Quit game |

## 🐛 Troubleshooting

**Game won't start:**
- Ensure pygame is installed: `pip install pygame`
- Check Python version is 3.8 or higher

**Sprites don't appear:**
- Verify `assets/` folder exists with `.png` files
- Check file names match sprite_name in code

**No sound:**
- Add audio files to `sounds/` folder
- Verify file formats (`.wav` for sound effects, `.mp3` for music)

## 📊 Window Size

The game window is 1000x700 pixels. To resize, change:
```python
WIDTH, HEIGHT = 1000, 700  # Line 11
```

## 🚀 Future Enhancements

- [ ] Status effects (burn, poison, paralysis)
- [ ] Special abilities/traits with battle effects
- [ ] Stat modifiers (attack up, defense down)
- [ ] More Pokémon types and moves
- [ ] Item system (potions, status heals)
- [ ] Multiplayer/Online support
- [ ] Better sprite graphics
- [ ] More sound effects and music tracks
- [ ] Save/load battle statistics
- [ ] Difficulty levels (Easy, Normal, Hard)
- [ ] Move categories (Physical, Special, Status)
- [ ] Critical hit chance system

## 📄 License

Open source - feel free to modify and improve!

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new Pokémon and moves
- Improve sprite graphics
- Add sound effects
- Optimize game balance
- Fix bugs

---

**Enjoy your retro Pokémon battles!** 🎮⚡
