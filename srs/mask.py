import pygame

light_mask = pygame.mask.Mask(size=(15000,15000), fill=False)
screen_mask = pygame.mask.Mask(size=(15000,15000), fill=True)

def get_shadow(screen, room, room_dest):
    # screen_mask = pygame.mask.from_surface(screen)
    light_mask.draw(pygame.mask.from_threshold(screen, (255, 0, 0), (35, 35, 35, 0)), (0,0))
    screen_mask.erase(light_mask, (0,0))
    return screen_mask.to_surface(surface=screen, setcolor=(0, 0, 0), unsetsurface=room, dest=room_dest)

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

def check_camera_wall_collisions(camera_box_surf, collision_mask, offset):
    pygame.draw.circle(camera_box_surf, (255, 0, 0), (camera_box_surf.get_width() // 2, camera_box_surf.get_height() // 2), camera_box_surf.get_height() // 2)
    camera_box_mask = pygame.mask.from_threshold(camera_box_surf, (255, 0, 0), (35, 35, 35, 0))
    return collision_mask.overlap_area(camera_box_mask, offset)