import pygame

class Door:
    def __init__(self, mask:pygame.Mask, coord:pygame.Vector2) -> None:
        self.mask = mask
        self.coord = coord
        self.is_open = False
        self.closed_hitbox_mask = pygame.Mask(size=(100,100))

    def trigger(self, collision_mask:pygame.Mask) -> None:
        if not(self.is_open):
            self.is_open = True
            self.closed_hitbox_mask = pygame.mask.Mask(size=self.mask.get_size(), fill=False)
            self.closed_hitbox_mask.draw(collision_mask, (-self.coord[0], -self.coord[1]))
            collision_mask.erase(self.mask, self.coord)
        else:
            self.is_open = False
            collision_mask.draw(self.closed_hitbox_mask, self.coord)
        print(self.is_open)


    @staticmethod
    def get_door_mask(surface:pygame.Surface) -> pygame.Mask:
        door_mask = pygame.mask.Mask(size=surface.get_size(), fill=False)
        door_mask.draw(pygame.mask.from_threshold(surface, (0, 0, 255), (1, 1, 1, 1)), (0, 0))
        return door_mask

    @staticmethod
    def get_doors(mask:pygame.Mask) -> list:
        doors = []
        acc = 20
        step = 15
        disposable_mask = pygame.mask.Mask(size=(acc, acc), fill=True)
        last_size = [acc, acc]
        temp_size = [acc, acc]
        for i in range(mask.get_size()[1] // acc):
            for j in range(mask.get_size()[0] // acc):
                if mask.overlap_area(disposable_mask, (j * acc, i * acc)):
                    temp_size = [temp_size[0], temp_size[1] + step]
                    while (mask.overlap_area(pygame.mask.Mask(temp_size, fill=True),(j * acc, i * acc)) - mask.overlap_area(pygame.mask.Mask(last_size, fill=True), (j * acc, i * acc))):
                        last_size = temp_size
                        temp_size = [temp_size[0], temp_size[1] + step]
                    temp_size = [temp_size[0] + step, temp_size[1]]
                    while (mask.overlap_area(pygame.mask.Mask(temp_size, fill=True), (j * acc, i * acc)) - mask.overlap_area(pygame.mask.Mask(last_size, fill=True), (j * acc, i * acc))):
                        last_size = temp_size
                        temp_size = [temp_size[0] + step, temp_size[1]]
                    door = Door(pygame.mask.Mask(size=temp_size, fill=False), pygame.Vector2(j * acc, i * acc))
                    door.mask.draw(mask, (j * -acc, i * -acc))
                    doors.append(door)
                    last_size = [acc, acc]
                    temp_size = [acc, acc]

        door_groups_list = []
        group_id = 0
        for door in doors:
            grouped = False
            for i in range(group_id):
                if door_groups_list[i][0].overlap_area(door.mask, (door.coord[0] - door_groups_list[i][1][0], door.coord[1] - door_groups_list[i][1][1])):
                    door_groups_list[i][0].draw(door.mask, (door.coord[0] - door_groups_list[i][1][0], door.coord[1] - door_groups_list[i][1][1]))
                    grouped = True
            if not grouped:
                door_groups_list.append([door.mask, door.coord])
                group_id += 1

        doors = []
        for x in door_groups_list:
            doors.append(Door(x[0], x[1]))
        return doors

    @staticmethod
    def check_door_click(door_mask:pygame.Mask, light_mask:pygame.Mask, pos:pygame.Vector2) -> bool:
        pos[0] = max(0, min(pos[0], light_mask.get_size()[0]-1))
        pos[1] = max(0, min(pos[1], light_mask.get_size()[1]-1))
        return door_mask.get_at(pos) and light_mask.get_at(pos) # type: ignore
