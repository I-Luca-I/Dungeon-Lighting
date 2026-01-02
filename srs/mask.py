import pygame
import json
# testing
import random
random.seed(210943)

with open("settings.json", "r") as file:
    room_settings = json.load(file)

saved_img = pygame.image.load(f"saves/save{room_settings['save_number']}.png")

light_mask = pygame.mask.Mask(size=(15000, 15000), fill=False)
screen_mask = pygame.mask.from_threshold(saved_img, (50, 50, 50), (1, 1, 1, 1))
light_texture_surface = pygame.Surface((15000, 15000), pygame.SRCALPHA)
light_texture_surface.blit(screen_mask.to_surface(unsetcolor=(0, 0, 0, 150), setcolor=(0, 0, 0)), (0, 0))

max_door_size = (200, 200)

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

def get_doors(door_surf, door_mask, door_test_surf):
    doors = {}
    acc = 20
    step = 15
    disposable_mask = pygame.mask.Mask(size=(acc, acc), fill=True)
    last_size = [acc, acc]
    temp_size = [acc, acc]
    for i in range(door_surf.get_height() // acc):
        for j in range(door_surf.get_width() // acc):
            if door_mask.overlap_area(disposable_mask, (j * acc, i * acc)):
                temp_size = [temp_size[0], temp_size[1] + step]
                while (door_mask.overlap_area(pygame.mask.Mask(temp_size, fill=True), (j * acc, i * acc)) - door_mask.overlap_area(pygame.mask.Mask(last_size, fill=True), (j * acc, i * acc))):
                    last_size = temp_size
                    temp_size = [temp_size[0], temp_size[1] + step]
                temp_size = [temp_size[0] + step, temp_size[1]]
                while (door_mask.overlap_area(pygame.mask.Mask(temp_size, fill=True), (j * acc, i * acc)) - door_mask.overlap_area(pygame.mask.Mask(last_size, fill=True), (j * acc, i * acc))):
                    last_size = temp_size
                    temp_size = [temp_size[0] + step, temp_size[1]]
                door = pygame.mask.Mask(size=temp_size, fill=False)
                door.draw(door_mask, (j * -acc, i * -acc))
                doors.update({(j * acc, i * acc): door})
                last_size = [acc, acc]
                temp_size = [acc, acc]

    door_groups_list = []
    group_id = 0
    for key in doors:
        grouped = False
        for i in range(group_id):
            if door_groups_list[i][0].overlap_area(doors[key], (key[0] - door_groups_list[i][1][0], key[1] - door_groups_list[i][1][1])):
                door_groups_list[i][0].draw(doors[key], (key[0] - door_groups_list[i][1][0], key[1] - door_groups_list[i][1][1]))
                grouped = True
        if not grouped:
            door_groups_list.append([doors[key], list(key)])
            group_id += 1

    doors = {}
    for x in door_groups_list:
        doors.update({tuple(x[1]): x[0]})
        # testing
        # door_test_surf.blit(x[0].to_surface(unsetcolor=None, setcolor=(random.randint(1, 255),random.randint(1, 255),random.randint(1, 255))), x[1])
        # pygame.draw.circle(door_test_surf, 'red', x[1], 2)
    return doors

def check_door_click(door_mask, pos):
    return door_mask.get_at(pos) and not screen_mask.get_at(pos)
