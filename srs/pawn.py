import token
import pygame, math

rays = 1000
no_iterrupt_offset = 10
extra_light = 5
sin_cache = []
cos_cache = []
for i in range(rays):
    sin_cache.append(math.sin(i * (2 * math.pi) / rays))
    cos_cache.append(math.cos(i * (2 * math.pi) / rays))

class Pawn:
    def __init__(self, position=(0,0), radius=100, img=None, size=None, zoom_factor=1, relative_hitbox_scale=3):
        self.position = position
        self.radius = radius
        self.endpoints = []
        
        img = pygame.image.load(img)
        self.texture = pygame.transform.rotozoom(
            img, 
            0, 
            (size / img.get_width()) * zoom_factor
        )
        self.hitbox_surface = pygame.surface.Surface(size=((self.texture.get_width() // relative_hitbox_scale), (self.texture.get_height() // relative_hitbox_scale)))
        
        self.moving = False
        self.mouse_offset = [0, 0]

    def update(self, surface, room, collision_mask, mask_offset):
        self.update_endpoints(room, collision_mask, mask_offset)
        self.draw_mask(surface)

    def draw(self, surface, offset):
        surface.blit(self.texture, (self.position[0] - self.texture.get_width() // 2, self.position[1] - self.texture.get_height() // 2))
        self.draw_rays(surface, offset)

    def update_endpoints(self, surface, collision_mask, mask_offset):
        # pxarray = pygame.PixelArray(surface)
        endpoints = []

        start = (self.position[0] - mask_offset[0], self.position[1] - mask_offset[1])
        previous_point_interrupted = False
        previous_point_distance = 0
        a = 0
        while a < rays:
            
            end = (
                max(0, min(int(start[0] + self.radius * cos_cache[a]), surface.get_width() - 1)),
                max(0, min(int(start[1] + self.radius * sin_cache[a]), surface.get_height() - 1))
            )

            if (start[0] != end[0]):
                m = float(start[1]-end[1])/float(start[0]-end[0])
            else:
                m = 2000
            
            q = start[1] - m*start[0]
            dx = abs(start[0]-end[0])
            dy = abs(start[1]-end[1])
            
            interrupt = False

            if(dx > dy):
                for i in range(start[0], end[0], 1 if end[0] > start[0] else -1):
                    if (collision_mask.get_at((i, int(m*i+q))) == 1):
                        endpoints.append([a, i, int(m*i+q)])
                        interrupt = True
                        break
            
            else:  
                for i in range(start[1], end[1], 1 if end[1] > start[1] else -1):
                    if (collision_mask.get_at((int((i-q)/m), i)) == 1):
                        endpoints.append([a, int((i-q)/m), i])
                        interrupt = True
                        break

            if (not(interrupt)):
                endpoints.append([a, end[0], end[1]])

            if (not(previous_point_interrupted) and interrupt):
                a -= previous_point_distance - 1 
            else:
                a += 1 if interrupt else no_iterrupt_offset

            previous_point_interrupted = interrupt            
            previous_point_distance = 1 if interrupt else no_iterrupt_offset
        
        endpoints.sort()
        for i in range(len(endpoints)):
            endpoints[i][1] = (endpoints[i-1][1] + endpoints[i][1] + endpoints[(i+1) % len(endpoints)][1]) / 3
            endpoints[i][2] = (endpoints[i-1][2] + endpoints[i][2] + endpoints[(i+1) % len(endpoints)][2]) / 3

        for i in range(len(endpoints)):
            endpoints[i][1] += extra_light * cos_cache[endpoints[i][0]]
            endpoints[i][2] += extra_light * sin_cache[endpoints[i][0]]

        self.endpoints = [(endpoints[_][1], endpoints[_][2]) for _ in range(len(endpoints))]
        self.endpoints_id = [0] * len(self.endpoints)
        id = 0
        
        for i in range(len(self.endpoints)):
            self.endpoints_id[i] = id
            if (math.sqrt((self.endpoints[i][0] - self.endpoints[(i+1)%len(self.endpoints)][0])**2 + (self.endpoints[i][1] - self.endpoints[(i+1)%len(self.endpoints)][1])**2) > 7):
                id += 1

        for ids in range(0, id):
            print(self.endpoints_id)
            print(self.endpoints_id.count(ids))
            while (self.endpoints_id.count(ids) < 50 and self.endpoints_id.count(ids) > 0):
                self.endpoints.pop(self.endpoints_id.index(ids))
                self.endpoints_id.pop(self.endpoints_id.index(ids))

    def draw_rays(self, surface, offset=(0,0)):
        for i in range(len(self.endpoints)):
            if (self.endpoints_id[i] % 2 == 0):
                pygame.draw.line(surface, (255, 0, 0), (self.position[0] - offset[0], self.position[1] - offset[1]), (self.endpoints[i][0], self.endpoints[i][1]))
            else:
                pygame.draw.line(surface, (0, 255, 0), (self.position[0] - offset[0], self.position[1] - offset[1]), (self.endpoints[i][0], self.endpoints[i][1]))

    def draw_mask(self, surface):
        if len(self.endpoints) > 2:
            pygame.draw.polygon(surface, (255, 0, 0), self.endpoints)

    def update_collision(self, wall_mask, offset):
        pygame.draw.circle(
            surface = self.hitbox_surface, 
            color = (255, 0, 0), 
            center = (self.hitbox_surface.get_width() // 2, self.hitbox_surface.get_height() // 2), 
            radius = self.hitbox_surface.get_height() // 2
        )

        camera_box_mask = pygame.mask.from_threshold(self.hitbox_surface, (255, 0, 0), (35, 35, 35, 0))
        return wall_mask.overlap_area(camera_box_mask, offset)

    def center_to_camera(self, camera, camera_offset):
        delta_x = int(self.position[0] - camera.get_width() / 2)
        delta_y = int(self.position[1] - camera.get_height() / 2)
        camera_offset[0] -= delta_x
        camera_offset[1] -= delta_y
        self.position = [self.position[0] - delta_x, self.position[1] - delta_y]
        self.moving = False