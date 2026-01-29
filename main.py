# TODO: Arrows shooting, power display
import math
import random
import pygame, sys
from potions import handle_typing, get_power, buy_ingredient, sell_ingredient
from battle import start_battle, SmallGoblin, Soldier, draw_tower

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
UI_PANEL_COLOR = (30, 30, 35)

STATE = "IDLE"
WAVE = 1
PASSWORD = ""
COINS = 200
INVENTORY = {
    "uppercase": 0,
    "special_characters": 0,
    "numbers": 0
}
WAVE_ENEMIES = pygame.sprite.Group()

SHOP_BUTTONS = {}
categories = ["uppercase", "special_characters", "numbers"]
start_x = 705
for i, cat in enumerate(categories):
    buy_rect = pygame.Rect(start_x + (i * 95), 330, 64, 64)
    sell_rect = pygame.Rect(start_x + (i * 95) + 5, 400, 50, 20)
    SHOP_BUTTONS[cat] = {"buy": buy_rect, "sell": sell_rect}


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

    for cat, rects in SHOP_BUTTONS.items():
        if 0 < INVENTORY[cat] <= 2:
            state = "quarter"
        elif 2 < INVENTORY[cat] <= 3:
            state = "half"
        elif INVENTORY[cat] > 3:
            state = "full"
        else:
            state = "empty"

        sprite = potion_assets[cat][state]
        screen.blit(sprite, (rects["buy"].x, rects["buy"].y))

        qty_bg = pygame.Rect(rects["buy"].x + 40, rects["buy"].y + 45, 25, 18)
        pygame.draw.rect(screen, (240, 220, 180), qty_bg, border_radius=5)
        qty_text = font.render(str(INVENTORY[cat]), True, (60, 40, 25))
        screen.blit(qty_text, (qty_bg.x + 5, qty_bg.y + 1))

        pygame.draw.rect(screen, (120, 50, 50), rects["sell"], border_radius=3)
        sell_lbl = font.render("SELL", True, (255, 255, 255))
        screen.blit(sell_lbl, (rects["sell"].x + 8, rects["sell"].y + 2))

    p_text = font_bold.render(f"POTION POWER              {power_val}", True, (30, 80, 30))
    screen.blit(p_text, (725, 300))

    input_box = pygame.Rect(700, 440, 260, 45)
    pygame.draw.rect(screen, (80, 60, 40), input_box, 2, border_radius=5)

    txt_surf = font.render(PASSWORD + "|", True, (40, 30, 20))
    screen.blit(txt_surf, (input_box.x + 10, input_box.y + 15))

    max_len = 4 + (WAVE * 2)
    limit_text = font_bold.render(f"Limit {len(PASSWORD)}/{max_len}", True, (100, 50, 50))
    screen.blit(limit_text, (710, 490))

def main():
    global STATE, PASSWORD, COINS, INVENTORY, WAVE_ENEMIES, WAVE
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Potion Defense")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont("Arial", 14)
    try:
        font_bold = pygame.font.Font("assets/Daydream.otf", 12)
    except:
        font_bold = pygame.font.SysFont("Arial", 18, bold=True)

    background = pygame.image.load('assets/background.png').convert()
    background = pygame.transform.scale(background, (1000, 600))
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

    while True:
        dt = clock.tick(60) / 1000
        screen.blit(background, (0, 0))
        draw_tower(screen)
        power_val = get_power(PASSWORD)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if STATE == "IDLE":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for cat, rects in SHOP_BUTTONS.items():
                        if rects["buy"].collidepoint(event.pos):
                            COINS, INVENTORY = buy_ingredient(cat, COINS, INVENTORY)
                        if rects["sell"].collidepoint(event.pos):
                            COINS, INVENTORY, PASSWORD = sell_ingredient(cat, COINS, INVENTORY, PASSWORD)

                max_len = 4 + (WAVE * 2)

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

        if STATE == "BATTLE":
            draw_title(screen, f"WAVE {WAVE}")
            WAVE_ENEMIES.update(dt)
            WAVE_ENEMIES.draw(screen)

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
                    if WAVE == 5:
                        STATE = "GAME OVER"
                    else: WAVE += 1
                else:
                    STATE = "DEFEAT"

        elif STATE == "DEFEAT":
            overlay = font_bold.render("DEFEATED! Press R to restart", True, (255, 0, 0))
            screen.blit(overlay, (300, 300))
            if pygame.key.get_pressed()[pygame.K_r]:
                COINS, STATE, PASSWORD, WAVE = 200, "IDLE", "", 1

        elif STATE == "IDLE":
            draw_title(screen, "Password Wizard")

        elif STATE == "GAME OVER":
            overlay = font_bold.render("VICTORY! Press R to restart", True, (255, 0, 0))
            screen.blit(overlay, (300, 300))
            if pygame.key.get_pressed()[pygame.K_r]:
                COINS, STATE, PASSWORD, WAVE = 200, "IDLE", "", 1

        draw_sidebar(screen, font_small, font_bold, power_val, SCROLL_IMG, POTION_SPRITES, STATIC_COIN)
        pygame.display.update()


if __name__ == '__main__':
    main()