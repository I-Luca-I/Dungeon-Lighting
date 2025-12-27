import pygame

light_mask = pygame.mask.Mask(size=(15000, 15000), fill=False)
screen_mask = pygame.mask.Mask(size=(15000, 15000), fill=True)
light_texture_surface = pygame.Surface((1920, 1080), pygame.SRCALPHA)

def get_shadow(screen, room, room_dest, light_text_dest, light_radius):
    # screen_mask = pygame.mask.from_surface(screen)
    light_mask.draw(pygame.mask.from_threshold(screen, (255, 0, 0), (35, 35, 35, 0)), (0,0))
    screen_mask.erase(light_mask, (0,0))
    unsetsurface = room.copy()
    pygame.draw.circle(light_texture_surface, (0,0,0,200), light_text_dest, radius=light_radius+3)
    pygame.draw.circle(light_texture_surface, (0, 0, 0, 150), light_text_dest, radius=light_radius*.9)
    unsetsurface.blit(light_texture_surface, (0,0))
    screen_mask.to_surface(surface=screen, setcolor=(0, 0, 0), unsetsurface=(unsetsurface), dest=room_dest)
    # screen_mask.to_surface(surface=screen, setsurface=room, unsetsurface=room, dest=room_dest)

def get_collision_mask(room, thresholds):
    collision_mask = pygame.mask.Mask(room.get_size(), False)
    pxarray = pygame.PixelArray(room)

    for x in range(room.get_width()):
        for y in range(room.get_height()):
            if (room.unmap_rgb(pxarray[x][y])[1] >= room.unmap_rgb(pxarray[x][y])[2] + thresholds["b"] and
                room.unmap_rgb(pxarray[x][y])[1] >= room.unmap_rgb(pxarray[x][y])[0] + thresholds["r"]
                ):
                collision_mask.set_at((x, y), 1)

    return collision_mask