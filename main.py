import pygame, sys
from battle import start_battle
from potions import get_power

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
BACKGROUND = (255, 255, 255)

STATE = "IDLE"
COINS = 50
WAVE = 1

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        match STATE:
            case "BATTLE":
                power = get_power()
                result = start_battle()
                if not result:
                    STATE = "DEFEAT"
            case "IDLE":
                pass
            case "DEFEAT":
                pass


        screen.fill(BACKGROUND)
        pygame.display.update()


if __name__ == '__main__':
    main()
    pygame.init()