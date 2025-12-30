import pygame
import json

with open("settings.json", "r") as file:
    room_settings = json.load(file)

saved_img = pygame.image.load(f"saves/save{room_settings['save_number']}.png")

light_mask = pygame.mask.Mask(size=(15000, 15000), fill=False)
screen_mask = pygame.mask.from_threshold(saved_img, (50, 50, 50), (1, 1, 1, 1))
light_texture_surface = pygame.Surface((15000, 15000), pygame.SRCALPHA)
light_texture_surface.blit(screen_mask.to_surface(unsetcolor=(0, 0, 0, 150), setcolor=(0, 0, 0)), (0, 0))

def get_shadow(screen, room, room_dest, light_text_dest, light_radius, pawn):
    # screen_mask = pygame.mask.from_surface(screen)
    light_mask.draw(pygame.mask.from_threshold(screen, (255, 0, 0), (35, 35, 35, 0)), (0,0))
    screen_mask.erase(light_mask, (0,0))
    unsetsurface = room.copy()
    pygame.draw.circle(light_texture_surface, (0, 0, 0, 150), light_text_dest, radius=light_radius+10)
    # pygame.draw.circle(light_texture_surface, (0, 0, 0, 150), light_text_dest, radius=light_radius*.9)
    pygame.draw.polygon(light_texture_surface, (0, 0, 0, 100), pawn.endpoints)
    unsetsurface.blit(light_texture_surface, (0,0))
    screen_mask.to_surface(surface=screen, setcolor=(0, 0, 0), unsetsurface=unsetsurface, dest=room_dest)
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
    save_mask = pygame.mask.Mask(size=(15000, 15000), fill=True)
    save_mask.erase(screen_mask, (0,0))
    return save_mask.to_surface(unsetcolor=(50,50,50), setsurface=room, dest=(0,0))

def get_door_mask(door_surf):
    door_mask = pygame.mask.Mask(size=(15000, 15000), fill=False)
    door_mask.draw(pygame.mask.from_threshold(door_surf, (0, 0, 255), (1, 1, 1, 1)), (0, 0))
    return door_mask

def get_doors(door_surf, door_mask):
    doors = {}
    max_door_size = (200, 200)
    disposable_mask = pygame.mask.Mask(size=(20, 20), fill=True)
    last_size = [20,20]
    temp_size = [25,25]
    for i in range(door_surf.get_height() // 20):
        for j in range(door_surf.get_width() // 20):
            if door_mask.overlap_area(disposable_mask, (j * 20, i * 20)) > 5:
                while door_mask.overlap_area(pygame.mask.Mask(temp_size, fill=True), (j * 20, i * 20)) > door_mask.overlap_area(pygame.mask.Mask(last_size, fill=True), (j * 20, i * 20)):
                    last_size = temp_size
                    temp_size = [temp_size[0] + 1, temp_size[1] + 1]
                door = pygame.mask.Mask(size=temp_size, fill=False)
                door.draw(door_mask, (j * 20, i * 20))
                doors.update({(j * 20, i * 20): door})
                last_size = [20,20]
                temp_size = [20,20]

    temp_doors = doors
    for key1 in doors:
        for key2 in doors:
            if doors[key2].overlap_area(doors[key1], (key1[0]-key2[0], key1[1]-key2[1])) > 0:
                doors[key1].draw(doors[key2], (key1[0]-key2[0], key1[1]-key2[1]))
                temp_doors.pop(key2)
    doors = temp_doors

    return doors

def check_door_click(door_mask, pos):
    return door_mask.get_at(pos) and not screen_mask.get_at(pos)
