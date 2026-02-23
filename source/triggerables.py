import pygame, json

class Triggerable:
    def __init__(self, masks:dict, coord:pygame.Vector2, states:dict) -> None:
        self.masks = masks  # esempio {"mask_description":mask}
        self.coord = coord
        self.states = states  # esempio {"proposition_description":state}

    @staticmethod
    def check_click(mask:pygame.Mask, shadow_mask:pygame.Mask, pos:pygame.Vector2) -> bool:
        pos[0] = max(0, min(pos[0], shadow_mask.get_size()[0]-1))
        pos[1] = max(0, min(pos[1], shadow_mask.get_size()[1]-1))
        return mask.get_at(pos) and shadow_mask.get_at(pos) # type: ignore

    @staticmethod
    def get_big_mask(surface:pygame.Surface, color:tuple) -> pygame.Mask:
        big_mask = pygame.mask.Mask(size=surface.get_size(), fill=False)
        big_mask.draw(pygame.mask.from_threshold(surface, color, (1, 1, 1, 1)), (0, 0))
        return big_mask

    @staticmethod
    def get_instances_list(big_mask, starting_states_dict) -> list:
        instances_list = []
        acc = 20
        step = 15
        disposable_mask = pygame.mask.Mask(size=(acc, acc), fill=True)
        last_size = [acc, acc]
        temp_size = [acc, acc]
        for i in range(big_mask.get_size()[1] // acc):
            for j in range(big_mask.get_size()[0] // acc):
                if big_mask.overlap_area(disposable_mask, (j * acc, i * acc)):
                    temp_size = [temp_size[0], temp_size[1] + step]
                    while (big_mask.overlap_area(pygame.mask.Mask(temp_size, fill=True),(j * acc, i * acc)) - big_mask.overlap_area(pygame.mask.Mask(last_size, fill=True), (j * acc, i * acc))):
                        last_size = temp_size
                        temp_size = [temp_size[0], temp_size[1] + step]
                    temp_size = [temp_size[0] + step, temp_size[1]]
                    while (big_mask.overlap_area(pygame.mask.Mask(temp_size, fill=True),(j * acc, i * acc)) - big_mask.overlap_area(pygame.mask.Mask(last_size, fill=True), (j * acc, i * acc))):
                        last_size = temp_size
                        temp_size = [temp_size[0] + step, temp_size[1]]
                    instance = Triggerable({"main_mask": pygame.mask.Mask(size=temp_size, fill=False)}, pygame.Vector2(j * acc, i * acc), dict(starting_states_dict))
                    instance.masks["main_mask"].draw(big_mask, (j * -acc, i * -acc))
                    instances_list.append(instance)
                    last_size = [acc, acc]
                    temp_size = [acc, acc]

        instance_groups_list = []
        group_id = 0
        for instance in instances_list:
            grouped = False
            for i in range(group_id):
                if instance_groups_list[i][0].overlap_area(instance.masks["main_mask"], (instance.coord[0] - instance_groups_list[i][1][0], instance.coord[1] - instance_groups_list[i][1][1])):
                    instance_groups_list[i][0].draw(instance.masks["main_mask"], (instance.coord[0] - instance_groups_list[i][1][0], instance.coord[1] - instance_groups_list[i][1][1]))
                    grouped = True
            if not grouped:
                instance_groups_list.append([instance.masks["main_mask"], instance.coord])
                group_id += 1

        instances_list = []
        for x in instance_groups_list:
            instances_list.append(Triggerable({"main_mask": x[0]}, x[1], dict(starting_states_dict)))
        return instances_list


class Stairs(Triggerable):
    def trigger(self, game_id:str, stairs_list:list, stairs_destinations:list) -> pygame.Vector2:
        self.id = stairs_list.index(self)
        self.destination = stairs_destinations[self.id]
        return pygame.Vector2(self.destination)

    @staticmethod
    def get_stairs_mask(surface:pygame.Surface) -> pygame.Mask:
        return Triggerable.get_big_mask(surface=surface, color=(255,0,0))

    @staticmethod
    def get_stairs(stairs_mask:pygame.Mask) -> list:
        stairs = []
        for instance in Triggerable.get_instances_list(stairs_mask, starting_states_dict={"triggered": False}):
            stairs.append(Stairs(masks=instance.masks, coord=instance.coord, states=instance.states))
        return stairs


class Door(Triggerable):
    def trigger(self, collision_mask:pygame.Mask) -> None:
        if not(self.states["is_open"]):
            self.states["is_open"] = True
            self.masks["collision_mask_backup"] = pygame.mask.Mask(size=self.masks["main_mask"].get_size(), fill=False)
            self.masks["collision_mask_backup"].draw(collision_mask, (-self.coord[0], -self.coord[1]))
            collision_mask.erase(self.masks["main_mask"], self.coord)
        else:
            self.states["is_open"] = False
            collision_mask.draw(self.masks["collision_mask_backup"], self.coord)

    @staticmethod
    def get_door_mask(surface: pygame.Surface) -> pygame.Mask:
        return Triggerable.get_big_mask(surface=surface, color=(0, 0, 255))

    @staticmethod
    def get_doors(door_mask: pygame.Mask) -> list:
        doors = []
        for instance in Triggerable.get_instances_list(door_mask, starting_states_dict={"is_open": False}):
            doors.append(Door(masks=instance.masks, coord=instance.coord, states=instance.states))
        return doors