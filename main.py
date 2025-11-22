import pygame
import sys
import random
import os
import math  # <-- for smooth idle movement

# ------------ BASIC SETUP ------------
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokémon Battle - Retro Edition")

CLOCK = pygame.time.Clock()

# ============ UI POSITION GUIDE ============
# SCREEN SIZE: 1000 x 700
# 
# BATTLE SCREEN LAYOUT:
# - Enemy info box: Top-right area (x=500, y=50, width=450, height=150)
# - Enemy sprite: (x=550, y=220)
# - Player info box: Bottom-left area (x=50, y=HEIGHT-180, width=450, height=150)
# - Player sprite: (x=150, y=140)
# - Message box: Center (x=50, y=420, width=WIDTH-100, height=120)
# - Attack buttons: Bottom area (y=520 for first row, y=577 for second row)
#
# To adjust positions, search for the values below:
# - Enemy Y position: 50, 220
# - Player Y position: HEIGHT-180, HEIGHT-105, HEIGHT-135, HEIGHT-170
# - Message box Y: 420
# - Attack buttons Y: 520, 577
# - Win screen Y: 570, 630
# ============================================

# Retro Color Palette (Game Boy inspired)
RETRO_BG = (155, 188, 15)      # Classic Game Boy green
RETRO_DARK = (81, 108, 32)     # Dark green
RETRO_LIGHT = (188, 220, 72)   # Light green
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 220, 0)
RED = (220, 0, 0)
GREY = (120, 120, 120)
LIGHT_GREY = (180, 180, 180)
YELLOW = (255, 255, 0)

# Fonts - Using default fonts for retro pixel look
FONT_TINY = pygame.font.SysFont("courier", 14, bold=True)
FONT_SMALL = pygame.font.SysFont("courier", 18, bold=True)
FONT_MED = pygame.font.SysFont("courier", 24, bold=True)
FONT_LARGE = pygame.font.SysFont("courier", 32, bold=True)
TITLE_FONT = pygame.font.SysFont("courier", 48, bold=True)

ASSETS_DIR = "assets"
SOUNDS_DIR = "sounds"

# ------------ SOUND HELPERS ------------

def safe_load_sound(name):
    path = os.path.join(SOUNDS_DIR, name)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None
    return None

HIT_SOUND = safe_load_sound("hit.wav")
SELECT_SOUND = safe_load_sound("select.wav")
FAINT_SOUND = safe_load_sound("faint.wav")

def play_sound(snd):
    if snd is not None:
        snd.play()

def play_bgm():
    path = os.path.join(SOUNDS_DIR, "bgm.mp3")
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

def stop_bgm():
    pygame.mixer.music.stop()

# ------------ CORE CLASSES ------------

class Move:
    def __init__(self, name, power, move_type):
        self.name = name
        self.power = power
        self.type = move_type  # "FIRE", "WATER", etc.

class Pokemon:
    def __init__(self, name, p_type, max_hp, attack, defense, speed, moves, sprite_name):
        self.name = name
        self.type = p_type
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.moves = moves          # list[Move]
        self.sprite_name = sprite_name
        self.sprite = self.load_sprite()

    @property
    def is_fainted(self):
        return self.current_hp <= 0

    def load_sprite(self):
        filename = f"{self.sprite_name}.png"
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (220, 220))
            return img
        # fallback: colored box
        surf = pygame.Surface((220, 220))
        surf.fill((random.randint(80, 200), random.randint(80, 200), random.randint(80, 200)))
        return surf

class Button:
    def __init__(self, rect, text, font, bg=LIGHT_GREY, fg=BLACK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg = bg
        self.fg = fg
        self.hover = False

    def draw(self, surface):
        # Retro button style with border
        color = (200, 200, 200) if self.hover else self.bg
        pygame.draw.rect(surface, color, self.rect, border_radius=0)
        pygame.draw.rect(surface, BLACK, self.rect, 3, border_radius=0)
        
        txt_surf = self.font.render(self.text, True, self.fg)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

# ------------ TYPE & DAMAGE ------------

TYPE_EFFECTIVENESS = {
    ("FIRE", "GRASS"): 2.0,
    ("WATER", "FIRE"): 2.0,
    ("GRASS", "WATER"): 2.0,
    ("ELECTRIC", "WATER"): 2.0,
    ("GRASS", "FIRE"): 0.5,
    ("FIRE", "WATER"): 0.5,
    ("WATER", "GRASS"): 0.5,
    ("ELECTRIC", "GRASS"): 0.5,
}

def type_multiplier(move_type, defender_type):
    return TYPE_EFFECTIVENESS.get((move_type, defender_type), 1.0)

def calc_damage(attacker, defender, move):
    # Balanced damage calculation - battles should last 3-5 turns
    base = move.power * 0.4 + attacker.attack * 0.3 - defender.defense * 0.4
    if base < 3:
        base = 3
    stab = 1.15 if move.type == attacker.type else 1.0
    mult = type_multiplier(move.type, defender.type)
    rand = random.uniform(0.9, 1.0)
    dmg = int(base * stab * mult * rand)
    if dmg < 1:
        dmg = 1
    return dmg, mult

# ------------ POKÉMON LIST ------------

def create_pokemons():
    # Moves
    flamethrower = Move("Flamethrower", 90, "FIRE")
    fire_blast = Move("Fire Blast", 110, "FIRE")
    ember = Move("Ember", 40, "FIRE")
    wing_attack = Move("Wing Attack", 60, "FIRE")   # treat as FIRE

    water_gun = Move("Water Gun", 40, "WATER")
    bubble_beam = Move("Bubble Beam", 65, "WATER")
    hydro_pump = Move("Hydro Pump", 110, "WATER")
    bite = Move("Bite", 60, "WATER")                # treat as WATER

    vine_whip = Move("Vine Whip", 45, "GRASS")
    razor_leaf = Move("Razor Leaf", 55, "GRASS")
    giga_drain = Move("Giga Drain", 75, "GRASS")
    seed_bomb = Move("Seed Bomb", 80, "GRASS")

    thunder_shock = Move("ThunderShock", 40, "ELECTRIC")
    thunderbolt = Move("Thunderbolt", 90, "ELECTRIC")
    volt_tackle = Move("Volt Tackle", 100, "ELECTRIC")
    quick_attack = Move("Quick Attack", 40, "ELECTRIC")  # treat as ELECTRIC

    shadow_ball = Move("Shadow Ball", 80, "GHOST")
    dark_pulse = Move("Dark Pulse", 80, "GHOST")
    sludge_bomb = Move("Sludge Bomb", 90, "GHOST")       # treat as GHOST
    night_shade = Move("Night Shade", 70, "GHOST")

    psychic = Move("Psychic", 90, "PSYCHIC")
    psybeam = Move("Psybeam", 65, "PSYCHIC")
    dazzling_gleam = Move("Dazzling", 80, "PSYCHIC")     # treat as PSYCHIC
    focus_blast = Move("Focus Blast", 120, "PSYCHIC")

    charizard = Pokemon(
        "Charizard", "FIRE", 220, 65, 60, 100,
        [flamethrower, wing_attack, fire_blast, ember],
        sprite_name="charizard"
    )

    blastoise = Pokemon(
        "Blastoise", "WATER", 230, 60, 75, 70,
        [water_gun, bubble_beam, hydro_pump, bite],
        sprite_name="blastoise"
    )

    venusaur = Pokemon(
        "Venusaur", "GRASS", 235, 62, 65, 70,
        [vine_whip, razor_leaf, giga_drain, seed_bomb],
        sprite_name="venusaur"
    )

    pikachu = Pokemon(
        "Pikachu", "ELECTRIC", 160, 45, 35, 110,
        [thunder_shock, thunderbolt, volt_tackle, quick_attack],
        sprite_name="pikachu"
    )

    gengar = Pokemon(
        "Gengar", "GHOST", 180, 70, 45, 110,
        [shadow_ball, dark_pulse, sludge_bomb, night_shade],
        sprite_name="gengar"
    )

    alakazam = Pokemon(
        "Alakazam", "PSYCHIC", 170, 75, 40, 120,
        [psychic, psybeam, dazzling_gleam, focus_blast],
        sprite_name="alakazam"
    )

    return [charizard, blastoise, venusaur, pikachu, gengar, alakazam]

# ------------ DRAW HELPERS ------------

def draw_hp_bar(pokemon, x, y, width=260, height=22):
    ratio = pokemon.current_hp / pokemon.max_hp
    ratio = max(0, min(1, ratio))

    pygame.draw.rect(WIN, BLACK, (x, y, width, height), border_radius=0)
    pygame.draw.rect(WIN, BLACK, (x, y, width, height), 2, border_radius=0)
    pygame.draw.rect(WIN, RED, (x + 2, y + 2, width - 4, height - 4), border_radius=0)
    pygame.draw.rect(WIN, GREEN, (x + 2, y + 2, int((width - 4) * ratio), height - 4), border_radius=0)

    hp_text = FONT_TINY.render(f"{pokemon.current_hp}/{pokemon.max_hp}", True, BLACK)
    WIN.blit(hp_text, (x + width + 10, y + 3))

def draw_text(text, x, y, font, color=WHITE):
    surf = font.render(text, True, color)
    WIN.blit(surf, (x, y))

def draw_wrapped_text(text, x, y, font, color=WHITE, max_width=760, line_gap=3):
    words = text.split(" ")
    lines = []
    current = ""

    for w in words:
        test = current + w + " "
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = w + " "
    lines.append(current)

    for i, line in enumerate(lines):
        surf = font.render(line, True, color)
        WIN.blit(surf, (x, y + i * (font.get_height() + line_gap)))

# ------------ ENEMY AI ------------

def enemy_choose_move(enemy, player):
    best_move = None
    best_score = -1
    for move in enemy.moves:
        mult = type_multiplier(move.type, player.type)
        score = move.power * mult
        if score > best_score:
            best_score = score
            best_move = move
    return best_move

# ------------ GAME STATES ------------

STATE_SELECT = "select"
STATE_BATTLE = "battle"
STATE_GAMEOVER = "gameover"

def main():
    pokemons = create_pokemons()

    # Background image
    bg_image = None
    bg_path = os.path.join(ASSETS_DIR, "bac8.png")
    if os.path.exists(bg_path):
        try:
            bg_image = pygame.image.load(bg_path).convert()
            bg_image = pygame.transform.smoothscale(bg_image, (WIDTH, HEIGHT))
        except Exception:
            bg_image = None

    state = STATE_SELECT
    player = None
    enemy = None

    # ====== SELECTION PANEL + BUTTON LAYOUT ======
    panel_margin_x = 60
    panel_width    = WIDTH - 2 * panel_margin_x
    panel_height   = 80
    panel_top      = HEIGHT - panel_height - 40
    panel_rect     = pygame.Rect(panel_margin_x, panel_top, panel_width, panel_height)

    btn_width  = 140
    btn_height = 40

    # space between buttons so they fit nicely inside panel
    spacing_x = (panel_width - len(pokemons) * btn_width) // (len(pokemons) + 1)

    select_buttons = []
    for i, p in enumerate(pokemons):
        x = panel_margin_x + spacing_x * (i + 1) + btn_width * i
        y = panel_top + (panel_height - btn_height) // 2
        rect = (x, y, btn_width, btn_height)
        select_buttons.append(Button(rect, p.name, FONT_SMALL))



    move_buttons = []
    info_message = "Choose your Pokémon"
    last_hit_message = ""
    winner_text = ""

    # animation timers (for hit shake)
    player_shake_timer = 0
    enemy_shake_timer = 0

    running = True

    while running:
        CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- SELECT SCREEN ---
            if state == STATE_SELECT:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    for idx, btn in enumerate(select_buttons):
                        if btn.is_clicked(pos):
                            play_sound(SELECT_SOUND)
                            player = pokemons[idx]
                            enemy_options = [p for p in pokemons if p is not player]
                            enemy = random.choice(enemy_options)

                            # Create move buttons (2x2 grid)
                            move_buttons = []
                            btn_width = 220
                            btn_height = 100
                            margin = 15
                            mb_start_x = 650         # LEFT POSITION of buttons
                            mb_start_y = 600       # TOP POSITION of first row (adjust to move buttons up/down)
                            for m_i, move in enumerate(player.moves):
                                row = m_i // 2      # Row 0 or 1
                                col = m_i % 2       # Column 0 or 1
                                x = mb_start_x + col * (btn_width + margin)
                                y = mb_start_y + row * (btn_height + margin)
                                move_buttons.append(Button((x, y, btn_width, btn_height), move.name, FONT_MED))

                            info_message = f"A wild {enemy.name} appeared!"
                            last_hit_message = ""
                            state = STATE_BATTLE
                            play_bgm()

            # --- BATTLE INPUT ---
            elif state == STATE_BATTLE:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not player.is_fainted and not enemy.is_fainted:
                        pos = event.pos
                        for idx, btn in enumerate(move_buttons):
                            if btn.is_clicked(pos):
                                play_sound(SELECT_SOUND)
                                move = player.moves[idx]
                                dmg, mult = calc_damage(player, enemy, move)
                                enemy.current_hp -= dmg
                                if enemy.current_hp < 0:
                                    enemy.current_hp = 0

                                if mult > 1.0:
                                    last_hit_message = f"{player.name} used {move.name}! It's super effective! (-{dmg})"
                                elif mult < 1.0:
                                    last_hit_message = f"{player.name} used {move.name}! It's not very effective... (-{dmg})"
                                else:
                                    last_hit_message = f"{player.name} used {move.name}! (-{dmg})"

                                play_sound(HIT_SOUND)
                                enemy_shake_timer = 12  # enemy gets hit animation

                                # Enemy faint check
                                if enemy.is_fainted:
                                    play_sound(FAINT_SOUND)
                                    info_message = f"{enemy.name} fainted!"
                                    winner_text = "You win!"
                                    state = STATE_GAMEOVER
                                    stop_bgm()
                                    break

                                # Enemy turn
                                pygame.time.delay(400)
                                emove = enemy_choose_move(enemy, player)
                                edmg, emult = calc_damage(enemy, player, emove)
                                player.current_hp -= edmg
                                if player.current_hp < 0:
                                    player.current_hp = 0

                                if emult > 1.0:
                                    last_hit_message += f" | Enemy {enemy.name} used {emove.name}! Super effective! (-{edmg})"
                                elif emult < 1.0:
                                    last_hit_message += f" | Enemy {enemy.name} used {emove.name}! Not very effective... (-{edmg})"
                                else:
                                    last_hit_message += f" | Enemy {enemy.name} used {emove.name}! (-{edmg})"

                                play_sound(HIT_SOUND)
                                player_shake_timer = 12  # player gets hit animation

                                if player.is_fainted:
                                    play_sound(FAINT_SOUND)
                                    info_message = f"{player.name} fainted!"
                                    winner_text = "You lost..."
                                    state = STATE_GAMEOVER
                                    stop_bgm()
                                break

            # --- GAME OVER INPUT ---
            elif state == STATE_GAMEOVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        pokemons = create_pokemons()
                        player = None
                        enemy = None
                        move_buttons = []
                        info_message = "Choose your Pokémon"
                        last_hit_message = ""
                        winner_text = ""
                        state = STATE_SELECT
                        player_shake_timer = 0
                        enemy_shake_timer = 0
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        # decrement shake timers
        if player_shake_timer > 0:
            player_shake_timer -= 1
        if enemy_shake_timer > 0:
            enemy_shake_timer -= 1

        # ------------ DRAW ------------
        if bg_image:
            WIN.blit(bg_image, (0, 0))
        else:
            WIN.fill(RETRO_BG)

        if state == STATE_SELECT:
            # --- Retro title bar with border ---
            pygame.draw.rect(WIN, RETRO_DARK, (0, 0, WIDTH, 140))
            pygame.draw.rect(WIN, BLACK, (0, 0, WIDTH, 140), 4)

            # title
            title_text = "POKEMON BATTLE"
            title_surf = TITLE_FONT.render(title_text, True, YELLOW)
            title_rect = title_surf.get_rect(center=(WIDTH // 2, 35))
            WIN.blit(title_surf, title_rect)

            # subtitle
            subtitle_text = "RETRO EDITION"
            sub_surf = FONT_MED.render(subtitle_text, True, WHITE)
            sub_rect = sub_surf.get_rect(center=(WIDTH // 2, 85))
            WIN.blit(sub_surf, sub_rect)

            # Instructions
            inst_surf = FONT_SMALL.render("CLICK POKEMON TO BATTLE", True, BLACK)
            inst_rect = inst_surf.get_rect(center=(WIDTH // 2, 120))
            WIN.blit(inst_surf, inst_rect)

            # ====== SPRITES DIRECTLY ABOVE BUTTONS ======
            sprite_size   = 120
            gap_sprite_to_panel = 15

            sprite_y = panel_top - gap_sprite_to_panel - sprite_size

            for i, p in enumerate(pokemons):
                btn = select_buttons[i]
                sprite_x = btn.rect.centerx - sprite_size // 2
                sprite_img = pygame.transform.smoothscale(p.sprite, (sprite_size, sprite_size))
                WIN.blit(sprite_img, (sprite_x, sprite_y))

            # ====== RETRO PANEL BEHIND BUTTON ROW ======
            pygame.draw.rect(WIN, RETRO_LIGHT, panel_rect, border_radius=0)
            pygame.draw.rect(WIN, BLACK, panel_rect, 4)

            # buttons inside the panel
            for btn in select_buttons:
                btn.draw(WIN)


        elif state in (STATE_BATTLE, STATE_GAMEOVER):
            # idle bobbing offsets
            t = pygame.time.get_ticks() / 200.0
            player_idle_offset = int(5 * math.sin(t))
            enemy_idle_offset = int(5 * math.sin(t + 1.0))

            # Draw battle arena with retro border
            pygame.draw.rect(WIN, RETRO_DARK, (20, 20, WIDTH-40, HEIGHT-40))
            pygame.draw.rect(WIN, BLACK, (20, 20, WIDTH-40, HEIGHT-40), 5)
            pygame.draw.rect(WIN, RETRO_BG, (30, 30, WIDTH-60, HEIGHT-60))
            
            # Enemy info box (top-right)
            # Adjust first number (500) to move left/right, second number (50) to move up/down
            enemy_box = pygame.Rect(700, 50, 450, 150)
            pygame.draw.rect(WIN, RETRO_LIGHT, enemy_box)
            pygame.draw.rect(WIN, BLACK, enemy_box, 3)
            
            draw_text(f"{enemy.name}", 720, 65, FONT_MED, BLACK)
            draw_text(f"Type: {enemy.type}", 720, 100, FONT_SMALL, BLACK)
            draw_hp_bar(enemy, 720, 130, width=350)

            # Enemy sprite position - adjust numbers to move sprite around
            enemy_x = 900         # LEFT/RIGHT position
            enemy_y = 220 + enemy_idle_offset  # UP/DOWN position (220 is base, add more to move down)
            if enemy_shake_timer > 0:
                enemy_x += random.randint(-4, 4)
                enemy_y += random.randint(-2, 2)
            WIN.blit(enemy.sprite, (enemy_x, enemy_y))

            # Player info box (bottom-left)
            # Adjust (50, HEIGHT-180) to move box - first number left/right, second number up/down from bottom
            player_box = pygame.Rect(50, HEIGHT-190, 450, 150)
            pygame.draw.rect(WIN, RETRO_LIGHT, player_box)
            pygame.draw.rect(WIN, BLACK, player_box, 3)
            
            # Player name and type text positions - adjust Y values to align with box
            draw_text(f"{player.name}", 70, HEIGHT-170, FONT_MED, BLACK)          # Name position
            draw_text(f"Type: {player.type}", 70, HEIGHT-135, FONT_SMALL, BLACK)  # Type position
            draw_hp_bar(player, 70, HEIGHT-105, width=350)                         # HP bar position

            # Player sprite position - adjust numbers to move sprite around
            player_x = 150        # LEFT/RIGHT position
            player_y = 220 + player_idle_offset  # UP/DOWN position (140 is base, add more to move down)
            if player_shake_timer > 0:
                player_x += random.randint(-4, 4)
                player_y += random.randint(-2, 2)
            WIN.blit(player.sprite, (player_x, player_y))

            # Message box (center) - moved down to give HP more space
            # Adjust second number (420) to move message box up/down
            msg_box = pygame.Rect(50, 420, WIDTH-100, 120)
            pygame.draw.rect(WIN, RETRO_LIGHT, msg_box)
            pygame.draw.rect(WIN, BLACK, msg_box, 3)

            # Message text positions - adjust Y values to position text inside box
            draw_wrapped_text(info_message, 70, 435, FONT_SMALL, BLACK, max_width=WIDTH-140)   # First message
            draw_wrapped_text(last_hit_message, 70, 470, FONT_TINY, BLACK, max_width=WIDTH-140)  # Second message

            if state == STATE_BATTLE:
                # Move buttons at bottom (2x2 grid)
                for i, btn in enumerate(move_buttons):
                    btn.draw(WIN)
            else:
                # Game over screen - adjust Y values to move text up/down
                draw_text(winner_text, 450, 1000, FONT_LARGE, BLACK)                           # Winner text position
                draw_text("Press R to restart or ESC to quit", 400, 1050, FONT_SMALL, BLACK)  # Instructions position

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()