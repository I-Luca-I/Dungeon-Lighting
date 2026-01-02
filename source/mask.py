import pygame
from . import pawn

class Masks:
    def __init__(self) -> None:
        pass
        
    @staticmethod
    def get_collision_mask(dungeon:pygame.Surface, thresholds:pygame.Color) -> pygame.Mask:
        collision_mask = pygame.mask.Mask(size=dungeon.get_size(), fill=False)
        pxarray = pygame.PixelArray(dungeon)

        for x in range(dungeon.get_width()):
            for y in range(dungeon.get_height()):
                if (dungeon.unmap_rgb(pxarray[x][y])[1] >= dungeon.unmap_rgb(pxarray[x][y])[2] + thresholds.b and # type: ignore
                    dungeon.unmap_rgb(pxarray[x][y])[1] >= dungeon.unmap_rgb(pxarray[x][y])[0] + thresholds.r     # type: ignore
                    ):
                    collision_mask.set_at((x, y), 1)

        return collision_mask
    
    @staticmethod
    def update_light(light_mask:pygame.Mask, pawn:pawn.Pawn) -> None:
        buffer = pygame.surface.Surface(light_mask.get_size(), flags=pygame.SRCALPHA)
        buffer.fill((0, 0, 0, 0))
        pygame.draw.polygon(buffer, (0, 0, 0, 255), pawn.endpoints)
        light_mask.draw(pygame.mask.from_surface(buffer), (0, 0))

    @staticmethod
    def draw_light(buffer:pygame.surface.Surface, light_mask:pygame.Mask, pawn:pawn.Pawn) -> None:
        shadow_overlay = pygame.surface.Surface(buffer.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(shadow_overlay, (0, 0, 0, 100), (0, 0, shadow_overlay.get_width(), shadow_overlay.get_height()))
        pygame.draw.polygon(shadow_overlay, (255, 255, 255, 0), pawn.endpoints)
        buffer.blit(source=light_mask.to_surface(surface=shadow_overlay, setsurface=shadow_overlay, unsetcolor=(0, 0, 0)), dest=(0, 0))
