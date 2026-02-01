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
    def update_light(shadow_mask:pygame.Mask, light_mask:pygame.Mask, pawn:pawn.Pawn) -> None:
        light_mask.clear()
        buffer = pygame.surface.Surface(light_mask.get_size(), flags=pygame.SRCALPHA)
        buffer.fill((0, 0, 0, 0))
        buffer_dest = pawn.position - pygame.Vector2(pawn.radius, pawn.radius)
        buffer_endpoints = []
        for v in pawn.endpoints:
            buffer_endpoints.append(v - buffer_dest)
        pygame.draw.polygon(buffer, (0, 0, 0, 255), buffer_endpoints)
        light_mask.draw(pygame.mask.from_surface(buffer), (0, 0))
        shadow_mask.draw(pygame.mask.from_surface(buffer), buffer_dest)

    @staticmethod
    def draw_light(buffer:pygame.surface.Surface, shadow_mask:pygame.Mask, light_mask:pygame.Mask, pawn:pawn.Pawn) -> None:
        # shadow_overlay = pygame.surface.Surface(buffer.get_size(), pygame.SRCALPHA)
        # pygame.draw.rect(shadow_overlay, (0, 0, 0, 100), (0, 0, shadow_overlay.get_width(), shadow_overlay.get_height()))
        # pygame.draw.polygon(shadow_overlay, (255, 255, 255, 0), pawn.endpoints)
        # buffer.blit(source=light_mask.to_surface(surface=shadow_overlay, setsurface=shadow_overlay, unsetcolor=(0, 0, 0)), dest=(0, 0))

        buffer_dest = pawn.position - pygame.Vector2(pawn.radius, pawn.radius)
        # shadow_overlay = pygame.surface.Surface(size=shadow_mask.get_size(), flags=pygame.SRCALPHA)
        # pygame.draw.rect(shadow_overlay, (0, 0, 0, 100), (0, 0, shadow_overlay.get_width(), shadow_overlay.get_height()))
        # shadow_overlay.blit(source=light_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=None), dest=buffer_dest)
        # buffer.blit(source=shadow_mask.to_surface(surface=shadow_overlay, setsurface=shadow_overlay, unsetcolor=(0, 0, 0)), dest=(0, 0))

        shadow_mask.erase(light_mask, buffer_dest)
        buffer.blit(source=shadow_mask.to_surface(setcolor=(0, 0, 0, 100), unsetcolor=None), dest=(0, 0))
        buffer.blit(source=light_mask.to_surface(setcolor=(255, 255, 255, 0), unsetcolor=None), dest=buffer_dest)
        shadow_mask.draw(light_mask, buffer_dest)
        buffer.blit(source=shadow_mask.to_surface(setcolor=None, unsetcolor=(0, 0, 0)), dest=(0, 0))
        