import pygame

def get_shadow(screen, room):
    screen_mask = pygame.mask.from_surface(screen)
    light_mask = pygame.mask.from_threshold(screen, (255, 0, 0), (35, 35, 35, 0))
    screen_mask.erase(light_mask, (0, 0))
    return screen_mask.to_surface(surface=screen, setcolor=(0, 0, 0), unsetsurface=room)

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