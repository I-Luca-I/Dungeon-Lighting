import pygame, json
from . import pawn

### REDO REDO REDO
with open("config/default.json", "r") as file:
    room_settings = json.load(file)
saved_img = pygame.image.load(f"saves/save_{room_settings['save_number']}.png")
screen_mask = pygame.mask.from_threshold(saved_img, (50, 50, 50), (1, 1, 1, 1))

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

def get_save_surface(room): ### REDO REDO REDO
    save_mask = pygame.mask.Mask(size=(15000, 15000), fill=True)
    save_mask.erase(screen_mask, (0,0))
    return save_mask.to_surface(unsetcolor=(50,50,50), setsurface=room, dest=(0,0))

def get_door_mask(door_surf): ### REDO
    door_mask = pygame.mask.Mask(size=(15000, 15000), fill=False)
    door_mask.draw(pygame.mask.from_threshold(door_surf, (0, 0, 255), (1, 1, 1, 1)), (0, 0))
    return door_mask

def get_doors(door_surf, door_mask): ### REDO
    doors = {}
    max_door_size = (200, 200)
    disposable_mask = pygame.mask.Mask(size=(20, 20), fill=True)
    last_size = [20,20]
    temp_size = [25,25]
    for i in range(door_surf.get_height() // 20):
        for j in range(door_surf.get_width() // 20):
            if door_mask.overlap_area(disposable_mask, (j * 20, i * 20)) > 5:
                while (door_mask.overlap_area(pygame.mask.Mask(temp_size, fill=True), (j * 20, i * 20)) - door_mask.overlap_area(pygame.mask.Mask(last_size, fill=True), (j * 20, i * 20))) != 0:
                    last_size = temp_size
                    temp_size = [temp_size[0] + 20, temp_size[1] + 20]
                door = pygame.mask.Mask(size=temp_size, fill=False)
                door.draw(door_mask, (j * -20, i * -20))
                doors.update({(j * 20, i * 20): door})
                last_size = [20,20]
                temp_size = [25,25]

    door_groups_list = [[pygame.mask.Mask(size=(10,10), fill=False), [0,0]]]
    group_id = 0
    for key in doors:
        grouped = False
        for i in range(group_id):
            if door_groups_list[i][0].overlap_area(doors[key], (key[0]-door_groups_list[i][1][0], key[1]-door_groups_list[i][1][1])):
                door_groups_list[i][0].draw(doors[key], (key[0]-door_groups_list[i][1][0], key[1]-door_groups_list[i][1][1]))
                grouped = True
        if not grouped:
            door_groups_list.append([doors[key], list(key)])
            group_id += 1
    door_groups_list_copy = door_groups_list.copy()
    for x in door_groups_list:
        if pygame.mask.Mask(max_door_size, fill=True).overlap_area(x[0], (0,0)) < 400:
            door_groups_list_copy.remove(x)
    door_groups_list = door_groups_list_copy

    return doors

def check_door_click(door_mask, pos): ### REDO
    return door_mask.get_at(pos) and not screen_mask.get_at(pos)