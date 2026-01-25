import pygame, sys
from potions import handle_typing, get_power, buy_ingredient, sell_ingredient

# Configuration
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
UI_PANEL_COLOR = (30, 30, 35)

# Game State
STATE = "IDLE"
PASSWORD = ""
COINS = 200
INVENTORY = {
    "uppercase": 0,
    "special_characters": 0,
    "numbers": 0
}

# Button Layout Setup
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 30
SHOP_BUTTONS = {}
categories = ["uppercase", "special_characters", "numbers"]

for i, cat in enumerate(categories):
    # Buy buttons on the left, Sell buttons on the right
    buy_rect = pygame.Rect(700, 100 + (i * 80), BUTTON_WIDTH, BUTTON_HEIGHT)
    sell_rect = pygame.Rect(800, 100 + (i * 80), BUTTON_WIDTH, BUTTON_HEIGHT)
    SHOP_BUTTONS[cat] = {"buy": buy_rect, "sell": sell_rect}


def main():
    global STATE, PASSWORD, COINS, INVENTORY
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Potion Brewer Pro")

    # Fonts
    font_small = pygame.font.SysFont("Arial", 14)
    font_bold = pygame.font.SysFont("Arial", 18, bold=True)

    clock = pygame.time.Clock()

    BACKGROUND = pygame.image.load('assets/background.png').convert()
    BACKGROUND = pygame.transform.scale(BACKGROUND, (1000, 600))

    while True:
        screen.blit(BACKGROUND, (0, 0))

        # 1. Event Handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if STATE == "IDLE":
                # Check for Mouse Clicks on Shop Buttons
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left Click
                        for cat, rects in SHOP_BUTTONS.items():
                            if rects["buy"].collidepoint(event.pos):
                                COINS, INVENTORY = buy_ingredient(cat, COINS, INVENTORY)

                            if rects["sell"].collidepoint(event.pos):
                                # This now updates the PASSWORD string by removing a character
                                COINS, INVENTORY, PASSWORD = sell_ingredient(cat, COINS, INVENTORY, PASSWORD)

                # Handle Text Input
                result = handle_typing(event, PASSWORD, INVENTORY)
                if result == "SUBMITTED":
                    final_power = get_power(PASSWORD)
                    print(f"BATTLE START! Potion Power: {final_power}")
                    STATE = "BATTLE"
                else:
                    PASSWORD = result

        # 2. Game Logic Updates
        if STATE == "BATTLE":
            # (Battle logic would go here)
            pass

        # 3. Drawing Logic
        draw_sidebar(screen, font_small, font_bold)

        pygame.display.update()
        clock.tick(60)


def draw_sidebar(screen, font, font_bold):
    # Draw Sidebar Background
    pygame.draw.rect(screen, UI_PANEL_COLOR, (680, 0, 320, WINDOW_HEIGHT))
    pygame.draw.line(screen, (100, 100, 100), (680, 0), (680, WINDOW_HEIGHT), 2)

    # Header: Wallet
    coin_text = font_bold.render(f"WALLET: {COINS} Coins", True, (255, 215, 0))
    screen.blit(coin_text, (700, 30))

    # Shop Section
    for cat, rects in SHOP_BUTTONS.items():
        # Ingredient Label
        clean_name = cat.replace('_', ' ').title()
        label = font.render(f"{clean_name} (Owned: {INVENTORY[cat]})", True, (255, 255, 255))
        screen.blit(label, (700, rects["buy"].y - 25))

        # Buy Button (Green)
        pygame.draw.rect(screen, (40, 120, 40), rects["buy"], border_radius=4)
        b_text = font.render("BUY", True, (255, 255, 255))
        screen.blit(b_text, (rects["buy"].x + 25, rects["buy"].y + 7))

        # Sell Button (Red)
        pygame.draw.rect(screen, (140, 40, 40), rects["sell"], border_radius=4)
        s_text = font.render("SELL", True, (255, 255, 255))
        screen.blit(s_text, (rects["sell"].x + 23, rects["sell"].y + 7))

    # Potion Display Area
    power_val = get_power(PASSWORD)
    power_text = font_bold.render(f"POTION POWER: {power_val}", True, (0, 255, 100))
    screen.blit(power_text, (700, 420))

    # Input Box Visual
    input_box_rect = pygame.Rect(700, 450, 260, 45)
    pygame.draw.rect(screen, (10, 10, 10), input_box_rect, border_radius=5)
    pygame.draw.rect(screen, (80, 80, 80), input_box_rect, 2, border_radius=5)

    # Text inside box
    txt_surf = font.render(PASSWORD + "|", True, (255, 255, 255))
    screen.blit(txt_surf, (input_box_rect.x + 10, input_box_rect.y + 15))

    help_text = font.render("Press ENTER to start battle", True, (150, 150, 150))
    screen.blit(help_text, (700, 505))


if __name__ == '__main__':
    main()