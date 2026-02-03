import pygame
from . import pawn, mask

class Chunk:
    def __init__(self, dungeon:pygame.Surface, size:pygame.Vector2, coord:pygame.Vector2):
        self.surface = pygame.Surface(size=size)
        self.surface.blit(dungeon, dest=-coord)
        self.size = size
        self.coord = coord

    def render(self, screen:pygame.Surface, shadow_mask:pygame.Mask, light_mask:pygame.Mask, pawn:pawn.Pawn):
        if self.coord[0] <= pawn.position[0] <= self.coords[0] + self.size[0] and self.coord[1] <= pawn.position[1] <= self.coords[1] + self.size[1]:
            mask.Masks.draw_light(self.surface, shadow_mask, light_mask, pawn)
            