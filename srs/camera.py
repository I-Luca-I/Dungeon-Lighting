import pygame, math

rays = 1000
no_iterrupt_offset = 10
sin_cache = []
cos_cache = []
for i in range(rays):
    sin_cache.append(math.sin(i * (2 * math.pi) / rays))
    cos_cache.append(math.cos(i * (2 * math.pi) / rays))

class Camera:
    def __init__(self, position=(0, 0), radius=100, decay=0):
        self.position = position
        self.radius = radius
        self.decay = decay

    def update(self, screen, room, collision_mask):
        self.update_endpoints(room, collision_mask)
        # self.draw_rays(screen)
        self.draw_mask(screen)
        self.radius = max(0, self.radius-self.decay)

    def update_endpoints(self, surface, collision_mask):
        # pxarray = pygame.PixelArray(surface)
        endpoints = []

        start = (self.position[0], self.position[1])
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
            endpoints[i][1] += 10 * cos_cache[endpoints[i][0]]
            endpoints[i][2] += 10 * sin_cache[endpoints[i][0]]

        self.endpoints = [(endpoints[_][1], endpoints[_][2]) for _ in range(len(endpoints))]

    def draw_rays(self, surface):
        for i in range(len(self.endpoints)):
            pygame.draw.line(surface, (255, 0, 0), self.position, self.endpoints[i])

    def draw_mask(self, surface):
        if len(self.endpoints) > 2:
            pygame.draw.polygon(surface, (255, 0, 0), self.endpoints)
