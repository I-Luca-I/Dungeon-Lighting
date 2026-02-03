import pygame
from . import pawn, mask

class Chunk:
    def __init__(self, dungeon:pygame.Surface, size:pygame.Vector2, coord:pygame.Vector2) -> None:
        self.surface = pygame.Surface(size=size)
        self.surface.blit(dungeon, dest=-coord)
        self.size = size
        self.coord = coord
        # self.updated = False

    def render(self, screen:pygame.Surface, shadow_mask:pygame.Mask, light_mask:pygame.Mask, pawn:pawn.Pawn):
        if light_mask.overlap_area(pygame.mask.Mask((200, 200), True), self.coord-pawn.position-(pawn.radius, pawn.radius)) == 0:
            return
        
        # mask.Masks.draw_light(self.surface, shadow_mask, light_mask, pawn)
            