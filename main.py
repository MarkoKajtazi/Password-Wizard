import random
import pygame, sys

from battle import start_battle, SmallGoblin, Soldier, draw_tower
from potions import get_power

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
BACKGROUND = (255, 255, 255)

STATE = "BATTLE"
COINS = 50
WAVE = 1

def main():
    global STATE
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    enemies = start_new_round()
    power = get_power()
    while True:
        dt = clock.tick(60) / 1000
        screen.fill(BACKGROUND)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        match STATE:
            case "BATTLE":
                draw_tower(screen)
                draw_enemies(enemies, dt, screen)
                enemies_done = 0

                for enemy in enemies:
                    if enemy.rect.x >= 400:
                        enemy.is_done = True
                        enemies_done += 1
                    if enemies_done == len(enemies):
                        result = start_battle(power, enemies)
                        if not result:
                            STATE = "DEFEAT"

            case "IDLE":
                pass
            case "DEFEAT":
                pass

        pygame.display.update()

def start_new_round():
    random_number_enemies = random.randint(3, 7)
    enemies = pygame.sprite.Group()

    for i in range(random_number_enemies):
        enemy_type = random.choice(["goblin", "soldier"])

        random_x = random.randint(-350, -75)
        random_y = random.randint(430, 470)

        if enemy_type == "goblin":
            enemy = SmallGoblin(random_x, random_y)
        else:
            enemy = Soldier(random_x, random_y)

        enemies.add(enemy)

    return enemies

def draw_enemies(enemies, dt, screen):
    enemies.update(dt)
    enemies.draw(screen)

if __name__ == '__main__':
    main()
    pygame.init()