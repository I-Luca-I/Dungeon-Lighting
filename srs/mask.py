import pygame

light_mask = pygame.mask.Mask(size=(15000, 15000), fill=False)
screen_mask = pygame.mask.Mask(size=(15000, 15000), fill=True)
light_texture_surface = pygame.Surface((15000, 15000), pygame.SRCALPHA)

def get_shadow(screen, room, room_dest, light_text_dest, light_radius, pawn):
    # screen_mask = pygame.mask.from_surface(screen)
    light_mask.draw(pygame.mask.from_threshold(screen, (255, 0, 0), (35, 35, 35, 0)), (0,0))
    screen_mask.erase(light_mask, (0,0))
    unsetsurface = room.copy()
    pygame.draw.circle(light_texture_surface, (0, 0, 0, 150), light_text_dest, radius=light_radius+10)
    # pygame.draw.circle(light_texture_surface, (0, 0, 0, 150), light_text_dest, radius=light_radius*.9)
    pygame.draw.polygon(light_texture_surface, (0, 0, 0, 100), pawn.endpoints)
    unsetsurface.blit(light_texture_surface, (0,0))
    screen_mask.to_surface(surface=screen, setcolor=(0, 0, 0), unsetsurface=(unsetsurface), dest=room_dest)
    # screen_mask.to_surface(surface=screen, setsurface=room, unsetsurface=room, dest=room_dest)

def reset_shadow(light_text_dest, light_radius):
    pygame.draw.circle(light_texture_surface, (0, 0, 0, 150), light_text_dest, radius=light_radius+10)

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

def get_save_surface(room):
    save_mask = pygame.mask.Mask(size=(10000, 10000))
    save_mask.draw(light_mask, (0,0))
    return save_mask.to_surface(unsetcolor=(50,50,50), setsurface=room, dest=(0,0))