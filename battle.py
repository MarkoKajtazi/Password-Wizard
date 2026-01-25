import pygame

ENTITY_ASSETS = {
    "dictionary_diver": 'assets/orc.png',
    "battering_ram": 'assets/battering.png',
    "social_spy": 'assets/social_spy.png',
}

ENTITY_POWERS = {
    "dictionary_diver": 10,
    "battering_ram": 15,
    "social_spy": 20,
}

ENTITY_VALUES = {
    "dictionary_diver": 10,
    "battering_ram": 15,
    "social_spy": 20,
}

class Entity:
    def __init__(self, entity_type):
        self.entity_type = entity_type
        self.full_sheet = pygame.image.load(ENTITY_ASSETS[entity_type]).convert_alpha()
        self.frame_width = 100
        self.frame_height = 100
        self.current_frame = 0
        self.action_row = 0  # Row 0: Idle, Row 1: Walk, Row 2: Attack, etc.

    def get_frame_rect(self):
        x = self.current_frame * self.frame_width
        y = self.action_row * self.frame_height
        return pygame.Rect(x, y, self.frame_width, self.frame_height)

    def draw(self, surface, pos):
        source_rect = self.get_frame_rect()
        surface.blit(self.full_sheet, pos, source_rect)

    def update(self, animation_speed=0.1):
        self.current_frame += animation_speed
        if self.current_frame >= 6:
            self.current_frame = 0




def start_battle():
    pass