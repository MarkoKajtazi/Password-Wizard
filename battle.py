import pygame
import random
import math
TOWER_IMG = None
ARROW_IMG = None

# Arrow type definitions
ARROW_TYPES = {
    "normal": {
        "damage": 5,              # Low damage (free ammo)
        "color": None,            # No tint
        "effect": None,
        "speed": 8
    },
    "power": {
        "damage": 8,              # Medium damage, fast
        "color": (255, 200, 100), # Orange/gold tint
        "effect": None,
        "speed": 10
    },
    "magic": {
        "damage": 6,              # Low damage but slows
        "color": (150, 100, 255), # Purple tint
        "effect": "slow",
        "speed": 8
    },
    "explosive": {
        "damage": 15,             # Highest damage, slow arrow
        "color": (255, 100, 100), # Red tint
        "effect": None,
        "speed": 6
    }
}


def tint_image(image, color):
    """Apply a color tint to an image."""
    tinted = image.copy()
    tinted.fill(color + (0,), special_flags=pygame.BLEND_RGB_ADD)
    return tinted


class Arrow(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_enemy, arrow_type="normal"):
        super().__init__()
        global ARROW_IMG

        if ARROW_IMG is None:
            arrow_surface = pygame.image.load(
                "assets/Tiny RPG Character/Arrow(Projectile)/Arrow01(32x32).png").convert_alpha()
            ARROW_IMG = pygame.transform.scale(arrow_surface, (64, 64))

        # Get arrow type properties
        self.arrow_type = arrow_type
        type_data = ARROW_TYPES.get(arrow_type, ARROW_TYPES["normal"])
        self.damage = type_data["damage"]
        self.effect = type_data["effect"]
        self.speed = type_data["speed"]

        # Apply color tint if specified
        if type_data["color"]:
            self.original_image = tint_image(ARROW_IMG, type_data["color"])
        else:
            self.original_image = ARROW_IMG

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.pos = [float(start_x), float(start_y)]
        self.target = target_enemy
        self.hit = False

    def update(self, dt):
        if self.target and not self.hit:
            # Calculate direction to target
            target_x = self.target.rect.centerx
            target_y = self.target.rect.centery

            dx = target_x - self.pos[0]
            dy = target_y - self.pos[1]
            dist = max(1, (dx**2 + dy**2)**0.5)

            # Calculate angle and rotate arrow to point toward target
            angle = math.degrees(math.atan2(-dy, dx))
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=self.rect.center)

            # Move toward target
            self.pos[0] += self.speed * dx / dist
            self.pos[1] += self.speed * dy / dist
            self.rect.center = (int(self.pos[0]), int(self.pos[1]))

            # Check if arrow reached target
            if abs(dx) < 20 and abs(dy) < 20:
                self.hit = True
                if hasattr(self.target, 'take_damage'):
                    self.target.take_damage(self.damage, self.effect)
                self.kill()

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
        self.health = self.power
        self.is_done = False
        self.base_speed = 1
        self.slow_timer = 0

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

    def take_damage(self, amount, effect=None):
        self.health -= amount
        if effect == "slow":
            self.slow_timer = 3.0  # Slowed for 3 seconds

    def update(self, dt):
        # Update slow timer
        if self.slow_timer > 0:
            self.slow_timer -= dt
            speed = self.base_speed * 0.4  # 60% slower when slowed
        else:
            speed = self.base_speed

        if not self.is_done:
            self.rect.x += speed
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
        self.health = self.power
        self.is_done = False
        self.base_speed = 1.5
        self.slow_timer = 0

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

    def take_damage(self, amount, effect=None):
        self.health -= amount
        if effect == "slow":
            self.slow_timer = 3.0  # Slowed for 3 seconds

    def update(self, dt):
        # Update slow timer
        if self.slow_timer > 0:
            self.slow_timer -= dt
            speed = self.base_speed * 0.4  # 60% slower when slowed
        else:
            speed = self.base_speed

        if not self.is_done:
            self.rect.x += speed
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