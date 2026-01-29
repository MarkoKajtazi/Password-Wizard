import pygame
import random
TOWER_IMG = None

class SmallGoblin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = "goblin"
        self.walk_sheet = pygame.image.load(
            "assets/Tiny RPG Character/Characters(100x100)/Orc/Orc/Orc.png").convert_alpha()
        self.attack_sheet = pygame.image.load(
            "assets/Tiny RPG Character/Characters(100x100)/Orc/Orc/Orc-Attack02.png").convert_alpha()

        self.power = 10
        self.value = 20
        self.is_done = False

        self.walk_frames = self.load_frames(self.walk_sheet, 8, 1)
        self.attack_frames = self.load_frames(self.attack_sheet, 6, 0)

        self.frames = self.walk_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.animation_speed = 0.20
        self.animation_timer = 0

    def load_frames(self, sheet, frame_count, row):
        frames = []
        for i in range(frame_count):
            rect = pygame.Rect(i * 100, row * 100, 100, 100)
            frame = sheet.subsurface(rect)
            frames.append(pygame.transform.scale(frame, (250, 220)))
        return frames

    def update(self, dt):
        if not self.is_done:
            self.rect.x += 2
            self.frames = self.walk_frames
        else:
            self.frames = self.attack_frames

        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]


class Soldier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = "soldier"
        self.walk_sheet = pygame.image.load(
            "assets/Tiny RPG Character/Characters(100x100)/Soldier/Soldier/Soldier.png").convert_alpha()
        self.attack_sheet = pygame.image.load(
            "assets/Tiny RPG Character/Characters(100x100)/Soldier/Soldier/Soldier-Attack02.png").convert_alpha()

        self.power = 15
        self.value = 25
        self.is_done = False

        self.walk_frames = self.load_frames(self.walk_sheet, 8, 1)
        self.attack_frames = self.load_frames(self.attack_sheet, 6, 0)

        self.frames = self.walk_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.animation_speed = 0.20
        self.animation_timer = 0

    def load_frames(self, sheet, frame_count, row):
        frames = []
        for i in range(frame_count):
            rect = pygame.Rect(i * 100, row * 100, 100, 100)
            frame = sheet.subsurface(rect)
            frames.append(pygame.transform.scale(frame, (200, 200)))
        return frames

    def update(self, dt):
        if not self.is_done:
            self.rect.x += 3
            self.frames = self.walk_frames
        else:
            self.frames = self.attack_frames

        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

def start_battle(power, enemies):
    temp_power = power
    for enemy in enemies:
        if enemy.power > temp_power:
            return False, 0
        else:
            temp_power -= enemy.power

    collective_value = sum(enemy.value for enemy in enemies)
    return True, collective_value


def draw_tower(screen):
    global TOWER_IMG

    if TOWER_IMG is None:
        tower_sheet = pygame.image.load("assets/pixel_defenders_project_assets/towers.png").convert_alpha()

        sheet_width, sheet_height = tower_sheet.get_size()
        cols = 4
        rows = 4
        tile_w = sheet_width // cols
        tile_h = sheet_height // rows
        crop_rect = pygame.Rect(0.65 * tile_w, 3 * tile_h, tile_w, tile_h)

        castle_subsurface = tower_sheet.subsurface(crop_rect)
        TOWER_IMG = pygame.transform.scale(castle_subsurface, (350, 300))

    screen.blit(TOWER_IMG, (400, 280))