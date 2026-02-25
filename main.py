import math
import random
import pygame, sys
from potions import handle_typing, get_power, buy_ingredient, sell_ingredient, POTION_PRICES_MAP
from battle import start_battle, SmallGoblin, Soldier, draw_tower, Arrow

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
UI_PANEL_COLOR = (30, 30, 35)

STATE = "MENU"
WAVE = 1
STORY_PANEL = 0  # Track which story panel to show (0 = none yet)
PASSWORD = ""
COINS = 200
INVENTORY = {
    "uppercase": 0,
    "special_characters": 0,
    "numbers": 0,
    "limit": 0
}
WAVE_ENEMIES = pygame.sprite.Group()
ARROWS = pygame.sprite.Group()
ARROW_SPAWN_TIMER = 0
ARROW_SPAWN_INDEX = 0

SHOP_BUTTONS = {}
categories = ["uppercase", "special_characters", "numbers"]
start_x = 700
for i, cat in enumerate(categories):
    base_x = start_x + (i * 95)
    buy_rect = pygame.Rect(base_x, 390, 38, 24)
    sell_rect = pygame.Rect(base_x + 40, 390, 38, 24)
    sprite_rect = pygame.Rect(base_x + 6, 305, 64, 64)
    SHOP_BUTTONS[cat] = {"buy": buy_rect, "sell": sell_rect, "sprite": sprite_rect}

# Limit buy button (below the input box)
LIMIT_BUTTON = pygame.Rect(850, 520, 100, 28)


def get_estimated_power():
    """Calculate estimated power needed to defeat the upcoming wave."""
    base_enemies = 3
    coef = 1.3
    num_min = math.floor(base_enemies * (coef ** (WAVE - 2)))
    num_max = math.ceil(base_enemies * (coef ** (WAVE - 1)))
    # Average enemy power (goblin=10, soldier=15), assume worst case with soldiers
    avg_power = 15
    return num_max * avg_power


def start_new_round():
    base_enemies = 3
    coef = 1.3
    num_min = math.floor(base_enemies * (coef ** (WAVE - 2)))
    num_max = math.ceil(base_enemies * (coef ** (WAVE - 1)))
    num = random.randint(num_min, num_max)
    group = pygame.sprite.Group()

    for _ in range(num):
        etype = random.choice(["goblin", "soldier"])
        rx, ry = random.randint(-350, -75), random.randint(430, 470)
        enemy = SmallGoblin(rx, ry) if etype == "goblin" else Soldier(rx, ry)
        group.add(enemy)

    return group


def get_sprite(sheet, column, row, scale_to=(64, 64)):
    image = pygame.Surface((32, 32), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (column * 32, row * 32, 32, 32))

    return pygame.transform.scale(image, scale_to)


def draw_title(screen, title_text):
    try:
        title_font = pygame.font.Font("assets/Daydream.otf", 32)
    except:
        title_font = pygame.font.SysFont("Arial", 60, bold=True)

    shadow_surf = title_font.render(title_text, False, (0, 0, 0))
    screen.blit(shadow_surf, (24, 24))

    title_surf = title_font.render(title_text, False, (255, 255, 255))
    screen.blit(title_surf, (20, 20))


def draw_sidebar(screen, font, font_bold, power_val, scroll_surf, potion_assets, current_coin_frame):
    sidebar_x = 660
    sidebar_width = 340

    scaled_scroll = pygame.transform.scale(scroll_surf, (sidebar_width, WINDOW_HEIGHT))
    screen.blit(scaled_scroll, (sidebar_x, 0))

    screen.blit(current_coin_frame, (700, 60))
    coin_text = font_bold.render(f"{COINS}", True, (255, 255, 255))
    screen.blit(coin_text, (740, 65))

    # Instructions
    instructions = [
        "Buy ingredients to",
        "unlock characters.",
        "",
        "Type your password",
        "and press ENTER to",
        "defend!"
    ]
    for i, line in enumerate(instructions):
        if line:
            instr_text = font_bold.render(line, True, (60, 40, 25))
            text_x = sidebar_x + (sidebar_width - instr_text.get_width()) // 2
            screen.blit(instr_text, (text_x, 110 + i * 22))

    # Shop section label
    # shop_label = font_bold.render("INGREDIENTS", True, (60, 40, 25))
    # label_x = sidebar_x + (sidebar_width - shop_label.get_width()) // 2
    # screen.blit(shop_label, (label_x, 255))

    potion_names = {
        "uppercase": "CAPS",
        "special_characters": "SPECIAL",
        "numbers": "NUMBERS",
    }

    for cat, rects in SHOP_BUTTONS.items():
        if 0 < INVENTORY[cat] <= 2:
            state = "quarter"
        elif 2 < INVENTORY[cat] <= 3:
            state = "half"
        elif INVENTORY[cat] > 3:
            state = "full"
        else:
            state = "empty"

        sprite_rect = rects["sprite"]

        # Draw potion name above sprite
        name_text = font_bold.render(potion_names[cat], True, (60, 40, 25))
        name_x = sprite_rect.x + (64 - name_text.get_width()) // 2
        screen.blit(name_text, (name_x, sprite_rect.y - 20))

        # Draw sprite
        sprite = potion_assets[cat][state]
        screen.blit(sprite, (sprite_rect.x, sprite_rect.y))

        # Draw quantity badge
        qty_bg = pygame.Rect(sprite_rect.x + 40, sprite_rect.y + 45, 25, 18)
        pygame.draw.rect(screen, (240, 220, 180), qty_bg, border_radius=5)
        qty_text = font.render(str(INVENTORY[cat]), True, (60, 40, 25))
        screen.blit(qty_text, (qty_bg.x + 5, qty_bg.y + 1))

        # Draw price below sprite
        price = POTION_PRICES_MAP[cat]
        price_text = font_bold.render(f"{price}C", True, (255, 255, 255))
        price_x = sprite_rect.x + (64 - price_text.get_width()) // 2
        screen.blit(price_text, (price_x, sprite_rect.y + 66))

        # Draw buy button (left)
        pygame.draw.rect(screen, (50, 120, 50), rects["buy"], border_radius=4)
        buy_lbl = font_bold.render("BUY", True, (255, 255, 255))
        buy_lbl_x = rects["buy"].x + (38 - buy_lbl.get_width()) // 2
        buy_lbl_y = rects["buy"].y + (24 - buy_lbl.get_height()) // 2
        screen.blit(buy_lbl, (buy_lbl_x, buy_lbl_y))

        # Draw sell button (right)
        pygame.draw.rect(screen, (120, 50, 50), rects["sell"], border_radius=4)
        sell_lbl = font_bold.render("SELL", True, (255, 255, 255))
        sell_lbl_x = rects["sell"].x + (38 - sell_lbl.get_width()) // 2
        sell_lbl_y = rects["sell"].y + (24 - sell_lbl.get_height()) // 2
        screen.blit(sell_lbl, (sell_lbl_x, sell_lbl_y))

    p_text = font_bold.render(f"POTION POWER              {power_val}", True, (30, 80, 30))
    screen.blit(p_text, (720, 440))

    input_box = pygame.Rect(700, 470, 260, 40)
    pygame.draw.rect(screen, (80, 60, 40), input_box, 2, border_radius=5)

    txt_surf = font.render(PASSWORD + "|", True, (40, 30, 20))
    screen.blit(txt_surf, (input_box.x + 10, input_box.y + 12))

    max_len = 4 + (WAVE * 2) + INVENTORY["limit"]
    limit_text = font_bold.render(f"Limit {len(PASSWORD)}/{max_len}", True, (100, 50, 50))
    screen.blit(limit_text, (710, 525))

    # Draw limit buy button
    pygame.draw.rect(screen, (50, 120, 50), LIMIT_BUTTON, border_radius=4)
    limit_btn_text = font_bold.render("BUY LIMIT 5", True, (255, 255, 255))
    btn_text_x = LIMIT_BUTTON.x + (LIMIT_BUTTON.width - limit_btn_text.get_width()) // 2
    btn_text_y = LIMIT_BUTTON.y + (LIMIT_BUTTON.height - limit_btn_text.get_height()) // 2
    screen.blit(limit_btn_text, (btn_text_x, btn_text_y))

def main():
    global STATE, PASSWORD, COINS, INVENTORY, WAVE_ENEMIES, WAVE, ARROWS, ARROW_SPAWN_TIMER, ARROW_SPAWN_INDEX, STORY_PANEL
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Potion Defense")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont("Arial", 14)
    try:
        font_bold = pygame.font.Font("assets/Daydream.otf", 10)
    except:
        font_bold = pygame.font.SysFont("Arial", 10, bold=True)

    background = pygame.image.load('assets/background.png').convert()
    background = pygame.transform.scale(background, (1000, 600))
    menu_background = pygame.image.load('assets/menu-background.png').convert()
    menu_background = pygame.transform.scale(menu_background, (1000, 1000))
    SCROLL_IMG = pygame.image.load('assets/scroll.png').convert_alpha()
    sheet_img = pygame.image.load('assets/potions.png').convert_alpha()

    coin_sheet = pygame.image.load('assets/coin.png').convert_alpha()
    static_coin_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
    static_coin_surf.blit(coin_sheet, (0, 0), (0, 0, 20, 20))
    STATIC_COIN = pygame.transform.scale(static_coin_surf, (30, 30))

    coin_frame_index = 0
    coin_anim_timer = 0

    POTION_SPRITES = {
        "uppercase": {
            "empty": get_sprite(sheet_img, 1, 0),
            "quarter": get_sprite(sheet_img, 4, 0),
            "half": get_sprite(sheet_img, 3, 0),
            "full": get_sprite(sheet_img, 2, 0)
        },
        "special_characters": {
            "empty": get_sprite(sheet_img, 1, 13),
            "quarter": get_sprite(sheet_img, 19, 13),
            "half": get_sprite(sheet_img, 18, 13),
            "full": get_sprite(sheet_img, 17, 13)
        },
        "numbers": {
            "empty": get_sprite(sheet_img, 1, 18),
            "quarter": get_sprite(sheet_img, 9, 18),
            "half": get_sprite(sheet_img, 8, 18),
            "full": get_sprite(sheet_img, 7, 18)
        }
    }

    # Load story panels
    STORY_PANELS = []
    for i in range(1, 5):
        try:
            panel = pygame.image.load(f'assets/story/panel {i}.png').convert_alpha()
            panel = pygame.transform.scale(panel, (250, 250))
            STORY_PANELS.append(panel)
        except:
            pass  # Panel not yet created

    # Menu button
    PLAY_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 - 100, 500, 200, 50)

    while True:
        dt = clock.tick(60) / 1000

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if STATE == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if PLAY_BUTTON.collidepoint(event.pos):
                        STATE = "STORY"
                        STORY_PANEL = 1

            elif STATE == "STORY":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    STORY_PANEL += 1
                    if STORY_PANEL > len(STORY_PANELS):
                        STATE = "IDLE"

            elif STATE == "IDLE":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for cat, rects in SHOP_BUTTONS.items():
                        if rects["buy"].collidepoint(event.pos) or rects["sprite"].collidepoint(event.pos):
                            COINS, INVENTORY = buy_ingredient(cat, COINS, INVENTORY)
                        if rects["sell"].collidepoint(event.pos):
                            COINS, INVENTORY, PASSWORD = sell_ingredient(cat, COINS, INVENTORY, PASSWORD)
                    # Handle limit button click
                    if LIMIT_BUTTON.collidepoint(event.pos):
                        COINS, INVENTORY = buy_ingredient("limit", COINS, INVENTORY)

                max_len = 4 + (WAVE * 2) + INVENTORY["limit"]

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_BACKSPACE, pygame.K_KP_ENTER, pygame.K_RETURN):
                        result = handle_typing(event, PASSWORD, INVENTORY)
                    elif len(PASSWORD) < max_len:
                        result = handle_typing(event, PASSWORD, INVENTORY)
                    else:
                        result = PASSWORD
                    if result == "SUBMITTED":
                        WAVE_ENEMIES = start_new_round()
                        STATE = "BATTLE"
                    else:
                        PASSWORD = result

        # Draw MENU state
        if STATE == "MENU":
            screen.blit(menu_background, (0, 0))
            try:
                title_font = pygame.font.Font("assets/Daydream.otf", 40)
            except:
                title_font = pygame.font.SysFont("Arial", 60, bold=True)
            title_text = "PASSWORD WIZARD"
            title_x = (WINDOW_WIDTH - title_font.size(title_text)[0]) // 2
            title_y = 40
            border_color = (0, 0, 0)
            border_size = 2
            # Draw border by rendering text at offsets
            for dx in range(-border_size, border_size + 1):
                for dy in range(-border_size, border_size + 1):
                    if dx != 0 or dy != 0:
                        border_surf = title_font.render(title_text, True, border_color)
                        screen.blit(border_surf, (title_x + dx, title_y + dy))
            # Draw main text on top
            title_surf = title_font.render(title_text, True, (255, 255, 255))
            screen.blit(title_surf, (title_x, title_y))

            # Draw play button
            pygame.draw.rect(screen, (50, 50, 100), PLAY_BUTTON, border_radius=8)
            play_text = font_bold.render("PLAY", True, (255, 255, 255))
            play_x = PLAY_BUTTON.x + (PLAY_BUTTON.width - play_text.get_width()) // 2
            play_y = PLAY_BUTTON.y + (PLAY_BUTTON.height - play_text.get_height()) // 2
            screen.blit(play_text, (play_x, play_y))

        # Draw STORY state
        elif STATE == "STORY":
            screen.fill((10, 10, 15))
            if STORY_PANEL <= len(STORY_PANELS):
                # Draw panels one by one (all panels up to current)
                # Equal spacing: (1000 - 2*250) / 3 = 167 horizontal, (600 - 2*250) / 3 = 33 vertical
                panel_positions = [
                    (167, 33),
                    (583, 33),
                    (167, 316),
                    (583, 316)
                ]
                for i in range(STORY_PANEL):
                    if i < len(STORY_PANELS):
                        screen.blit(STORY_PANELS[i], panel_positions[i])

                # Draw "Click to continue" hint
                hint_text = font_bold.render("Click to continue", True, (150, 150, 150))
                screen.blit(hint_text, (WINDOW_WIDTH // 2 - hint_text.get_width() // 2, 570))

        # Draw game states (IDLE, BATTLE, DEFEAT, GAME OVER)
        if STATE in ("IDLE", "BATTLE", "DEFEAT", "GAME OVER"):
            screen.blit(background, (0, 0))
            draw_tower(screen)
            power_val = get_power(PASSWORD)

            if STATE == "BATTLE":
                draw_title(screen, f"WAVE {WAVE}")
                WAVE_ENEMIES.update(dt)
                WAVE_ENEMIES.draw(screen)

                # Spawn arrows toward enemies
                ARROW_SPAWN_TIMER += dt
                enemy_list = list(WAVE_ENEMIES)
                if ARROW_SPAWN_TIMER >= 0.15 and ARROW_SPAWN_INDEX < len(enemy_list):
                    target_enemy = enemy_list[ARROW_SPAWN_INDEX]
                    arrow = Arrow(520, 350, target_enemy)
                    ARROWS.add(arrow)
                    ARROW_SPAWN_INDEX += 1
                    ARROW_SPAWN_TIMER = 0

                # Update and draw arrows, respawn arrows that hit their target
                arrows_to_respawn = []
                for arrow in ARROWS:
                    if arrow.target and not arrow.hit:
                        dx = arrow.target.rect.centerx - arrow.pos[0]
                        dy = arrow.target.rect.centery - arrow.pos[1]
                        # Check if arrow will hit this frame (same condition as in Arrow.update)
                        if abs(dx) < 20 and abs(dy) < 20:
                            arrows_to_respawn.append(arrow.target)
                ARROWS.update(dt)
                for target in arrows_to_respawn:
                    if target and not target.is_done:
                        new_arrow = Arrow(520, 350, target)
                        ARROWS.add(new_arrow)
                ARROWS.draw(screen)

                enemies_done = 0

                for enemy in WAVE_ENEMIES:
                    if enemy.rect.x >= 400:
                        enemy.is_done = True
                        enemies_done += 1

                if enemies_done == len(WAVE_ENEMIES) and len(WAVE_ENEMIES) > 0:
                    success, collected_coins = start_battle(power_val, WAVE_ENEMIES)
                    if success:
                        COINS += collected_coins
                        STATE, PASSWORD = "IDLE", ""
                        ARROWS.empty()
                        ARROW_SPAWN_INDEX = 0
                        if WAVE == 5:
                            STATE = "GAME OVER"
                        else:
                            WAVE += 1
                    else:
                        STATE = "DEFEAT"
                        ARROWS.empty()
                        ARROW_SPAWN_INDEX = 0

            elif STATE == "DEFEAT":
                overlay = font_bold.render("DEFEATED! Press R to restart", True, (255, 0, 0))
                screen.blit(overlay, (300, 300))
                if pygame.key.get_pressed()[pygame.K_r]:
                    COINS, STATE, PASSWORD, WAVE = 200, "IDLE", "", 1
                    INVENTORY["uppercase"] = 0
                    INVENTORY["special_characters"] = 0
                    INVENTORY["numbers"] = 0
                    INVENTORY["limit"] = 0
                    ARROWS.empty()
                    ARROW_SPAWN_INDEX = 0
                    WAVE_ENEMIES.empty()
                    ARROW_SPAWN_TIMER = 0

            elif STATE == "IDLE":
                estimated = get_estimated_power()
                draw_title(screen, f"WAVE POWER IS {estimated}")

            elif STATE == "GAME OVER":
                overlay = font_bold.render("VICTORY! Press R to restart", True, (255, 0, 0))
                screen.blit(overlay, (300, 300))
                if pygame.key.get_pressed()[pygame.K_r]:
                    COINS, STATE, PASSWORD, WAVE = 200, "IDLE", "", 1
                    INVENTORY["uppercase"] = 0
                    INVENTORY["special_characters"] = 0
                    INVENTORY["numbers"] = 0
                    INVENTORY["limit"] = 0
                    ARROWS.empty()
                    ARROW_SPAWN_INDEX = 0
                    WAVE_ENEMIES.empty()
                    ARROW_SPAWN_TIMER = 0

            draw_sidebar(screen, font_small, font_bold, power_val, SCROLL_IMG, POTION_SPRITES, STATIC_COIN)

        pygame.display.update()


if __name__ == '__main__':
    main()