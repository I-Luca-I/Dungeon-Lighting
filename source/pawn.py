import pygame, math

sin_cache = []
cos_cache = []


class Pawn:
    def __init__(self, position:pygame.Vector2, radius:float, img:pygame.Surface, size:float) -> None:
        global sin_cache
        global cos_cache
        self.position = position
        self.radius = radius
        self.endpoints = []
        
        self.texture = pygame.transform.rotozoom(
            surface=img, 
            angle=0, 
            scale=size/img.get_width()
        )
        hitbox_surface = pygame.surface.Surface(size=(self.texture.get_width(), self.texture.get_height()))
        hitbox_surface.fill((0, 0, 0, 0))
        pygame.draw.circle(
            surface=hitbox_surface,
            color=(255, 255, 255, 255),
            center=(self.texture.get_width()//2, self.texture.get_height()//2),
            radius=self.texture.get_width()//4
        )
        self.hitbox = pygame.mask.from_threshold(surface=hitbox_surface, color=(255, 255, 255), threshold=(1, 1, 1))

        self.max_rays = 500 # The higher => the more detailed the shape will be
        self.smoothness = 5 # The lower => the more detailed the shape will be (better to lower this than to raise max_rays performance-wise)
        self.penetration = 3 # How much will it travel through walls

        self.moving = False
        self.mouse_offset = [0, 0]

        for i in range(self.max_rays):
            sin_cache.append(math.sin(i * (2 * math.pi) / self.max_rays))
            cos_cache.append(math.cos(i * (2 * math.pi) / self.max_rays))

    def update(self, collision_mask:pygame.Mask) -> None:
        self.position[0] = max(0, min(self.position[0], collision_mask.get_size()[0]-1))
        self.position[1] = max(0, min(self.position[1], collision_mask.get_size()[1]-1))
        self.update_endpoints(collision_mask)

    def update_endpoints(self, collision_mask:pygame.Mask) -> None:
        endpoints = []
        i = 0
        while i < self.max_rays:
            start = self.position
            end = (
                max(0, min(int(start[0] + (self.radius * cos_cache[i])), collision_mask.get_size()[0] - 1)),
                max(0, min(int(start[1] + (self.radius * sin_cache[i])), collision_mask.get_size()[1] - 1))
            )

            m = float(start[1]-end[1])/float(start[0]-end[0]) if (start[0] != end[0]) else collision_mask.get_size()[1]
            q = start[1] - m*start[0]
            dx = abs(start[0]-end[0])
            dy = abs(start[1]-end[1])
            
            interrupt = False

            if(dx > dy):
                for j in range(int(start[0]), int(end[0]), 1 if end[0] > start[0] else -1):
                    if (collision_mask.get_at((j, int(m*j+q))) == 1):
                        endpoints.append([i, j, int(m*j+q)])
                        interrupt = True
                        break
            else:  
                for j in range(int(start[1]), int(end[1]), 1 if end[1] > start[1] else -1):
                    if (collision_mask.get_at((int((j-q)/m), j)) == 1):
                        endpoints.append([i, int((j-q)/m), j])
                        interrupt = True
                        break

            if (not(interrupt)):
                endpoints.append([i, end[0], end[1]])

            i += 1 if interrupt else self.smoothness
        
        endpoints.sort()
        # for i in range(len(endpoints)):
        #     endpoints[i][1] = (endpoints[i-1][1] + endpoints[i][1] + endpoints[(i+1) % len(endpoints)][1]) / 3
        #     endpoints[i][2] = (endpoints[i-1][2] + endpoints[i][2] + endpoints[(i+1) % len(endpoints)][2]) / 3

        # for i in range(len(endpoints)):
        #     endpoints[i][1] += self.penetration * cos_cache[i]
        #     endpoints[i][2] += self.penetration * sin_cache[i]

        self.endpoints = [(endpoints[_][1], endpoints[_][2]) for _ in range(len(endpoints))]
    
    def handle_events(self, event:pygame.event.Event, mouse_coords:pygame.Vector2, collision_mask:pygame.Mask) -> None:
        self.move(event, mouse_coords, collision_mask)

    def move(self, event:pygame.event.Event, mouse_coords:pygame.Vector2, collision_mask:pygame.Mask) -> None:
        x = (mouse_coords[0] - self.position[0] + self.texture.get_width()//2)
        y = (mouse_coords[1] - self.position[1] + self.texture.get_height()//2)
        
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 0 <= x < self.texture.get_size()[0] and  0 <= y < self.texture.get_size()[1]):
            self.moving = True
            self.mouse_offset = self.position - mouse_coords
        elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1):
            self.moving = False

        x = (mouse_coords[0] - self.position[0])
        y = (mouse_coords[1] - self.position[1])

        self.mouse_endpoints = []
        self.mouse_startpoints = []
        for i in range(0, self.max_rays, self.max_rays//500):
            end = mouse_coords
            start = (
                max(0, min(int(end[0] - ((math.sqrt(x**2 + y**2)+10) * cos_cache[i])), collision_mask.get_size()[0] - 1)),
                max(0, min(int(end[1] - ((math.sqrt(x**2 + y**2)+10) * sin_cache[i])), collision_mask.get_size()[1] - 1))
            )
            self.mouse_startpoints.append(start)

            m = float(start[1]-end[1])/float(start[0]-end[0]) if (start[0] != end[0]) else collision_mask.get_size()[1]
            q = start[1] - m*start[0]
            dx = abs(start[0]-end[0])
            dy = abs(start[1]-end[1])

            interrupt = False
            
            if(dx > dy):
                for j in range(int(start[0]), int(end[0]), 1 if end[0] > start[0] else -1):
                    if (collision_mask.get_at((j, int(m*j+q))) == 1):
                        prev_j = j - (1 if end[0] > start[0] else -1)
                        self.mouse_endpoints.append([prev_j, int(m*(prev_j)+q)])
                        interrupt = True
                        break
            else:  
                for j in range(int(start[1]), int(end[1]), 1 if end[1] > start[1] else -1):
                    if (collision_mask.get_at((int((j-q)/m), j)) == 1):
                        prev_j = j - (1 if end[0] > start[0] else -1)
                        self.mouse_endpoints.append([int(((prev_j)-q)/m), prev_j])
                        interrupt = True
                        break

            if (not(interrupt)):
                self.mouse_endpoints.append([end[0], end[1]])

        i = 0
        self.interrupt_points = []
        self.start_interrupt_points = []
        while (i < len(self.mouse_endpoints)):
            start = self.position
            end = self.mouse_endpoints[i]

            m = float(start[1]-end[1])/float(start[0]-end[0]) if (start[0] != end[0]) else collision_mask.get_size()[1]
            q = start[1] - m*start[0]
            dx = abs(start[0]-end[0])
            dy = abs(start[1]-end[1])

            interrupt = False
            if(dx > dy):
                for j in range(int(start[0]), int(end[0]), 1 if end[0] > start[0] else -1):
                    if (collision_mask.get_at((j, int(m*j+q))) == 1):
                        self.interrupt_points.append((j, int(m*j+q)))
                        interrupt = True
                        break
            else:  
                for j in range(int(start[1]), int(end[1]), 1 if end[1] > start[1] else -1):
                    if (collision_mask.get_at((int((j-q)/m), j)) == 1):
                        self.interrupt_points.append((int((j-q)/m), j))
                        interrupt = True
                        break
            
            if (interrupt):
                self.mouse_startpoints.pop(i)
                self.mouse_endpoints.pop(i)
                self.start_interrupt_points.append(start)
            else:
                i += 1

        self.min_dist_index = 0
        for i in range(len(self.mouse_endpoints)):
            dist = abs(mouse_coords[0]-self.mouse_endpoints[i][0]) + abs(mouse_coords[1]-self.mouse_endpoints[i][1])
            min_dist = abs(mouse_coords[0]-self.mouse_endpoints[self.min_dist_index][0]) + abs(mouse_coords[1]-self.mouse_endpoints[self.min_dist_index][1])
            if (dist < min_dist):
                self.min_dist_index = i

        self.offset = pygame.Vector2(0,0)
        # self.overlap_mask = pygame.Mask(self.hitbox.get_size())
        # self.overlap_vector = None
        if (self.moving and len(self.mouse_endpoints) > 0):
            self.position = pygame.Vector2 (
                self.mouse_endpoints[self.min_dist_index][0] + self.mouse_offset[0],
                self.mouse_endpoints[self.min_dist_index][1] + self.mouse_offset[1]
            )

        self.overlap_mask = self.hitbox.overlap_mask(
            collision_mask,
            -(self.position - pygame.Vector2(self.texture.get_width()//2, self.texture.get_height()//2))
        )

        self.overlap_vector = [0,0]
        k = 0
        for i  in range(self.overlap_mask.get_size()[0]): 
            for j in range(self.overlap_mask.get_size()[1]): #type: ignore
                if self.overlap_mask.get_at((i,j)):
                    k += 1
                    self.overlap_vector[0] += i
                    self.overlap_vector[1] += j
        if k > 0:
            self.overlap_vector = (self.overlap_vector[0]//k, self.overlap_vector[1]//k)
        
        self.overlap_vector += self.position - pygame.Vector2(self.texture.get_width()//2, self.texture.get_height()//2)

        self.offset = (self.position - self.overlap_vector)
        if k == 0:
            self.offset = pygame.Vector2(0, 0)
        
        self.position += self.offset * 1.5


        # ho fatto questa modifica al check di line of sight, scala male con la grandezza del dungeon ma è fatta apposta per fixare il problema del movimento
        # che si presentava con i muri da pochi pixel, quindi una volta fatti i chunk offre la possibilità di usare mappe di risoluzione bassa come Labyrinth_2
        # con performance non impattata affatto
        # line_of_sight = pygame.surface.Surface(size=collision_mask.get_size(), flags=pygame.SRCALPHA)
        # versore_perpendicolare = pygame.Vector2(1,1)
        # if (math.sqrt((mouse_coords[0]-self.position[0])**2+(mouse_coords[1]-self.position[1])**2)) != 0:
        #     versore_perpendicolare = pygame.Vector2(-(mouse_coords[1]-self.position[1]), (mouse_coords[0]-self.position[0]))*(1/(math.sqrt((mouse_coords[0]-self.position[0])**2+(mouse_coords[1]-self.position[1])**2)))
        # semibase = 2  # da fare un modo dinamico (basato sulla grandezza del dungeon) per calcolarla (la semibase)
        # pygame.draw.line(line_of_sight, (0, 255, 0, 255), self.position, mouse_coords)
        # for i in range(1, semibase):
        #     pygame.draw.line(line_of_sight, (0, 255, 0, 255), self.position + versore_perpendicolare * i, mouse_coords + versore_perpendicolare * i)
        #     pygame.draw.line(line_of_sight, (0, 255, 0, 255), self.position - versore_perpendicolare * i, mouse_coords - versore_perpendicolare * i)
        # if (
        #     self.moving and 
        #     collision_mask.overlap_area(self.hitbox, mouse_coords + self.mouse_offset - (self.texture.get_width()//2, self.texture.get_height()//2)) < (semibase*2 -1) and
        #     collision_mask.overlap_area(pygame.mask.from_surface(line_of_sight), (0, 0)) < (semibase*2 -1)  # semibase*2 -1 = numero di raggi paralleli della line of sight

        # ):
        #     self.position = pygame.Vector2(mouse_coords[0] + self.mouse_offset[0], mouse_coords[1] + self.mouse_offset[1])

        # self.polygon_surface = pygame.surface.Surface(size=collision_mask.get_size())
        # if len(self.endpoints) > 2:
        #     pygame.draw.polygon(self.polygon_surface, (255,0,0,255), self.endpoints)
        
        # if (self.moving and collision_mask.overlap_area(self.hitbox, mouse_coords + self.mouse_offset - (self.texture.get_width()//2, self.texture.get_height()//2)) < 50 and self.polygon_surface.get_at((int(mouse_coords[0] + self.mouse_offset[0]), int(mouse_coords[1] + self.mouse_offset[1])))) == (255, 0, 0, 255):
        #     self.position = pygame.Vector2(mouse_coords[0] + self.mouse_offset[0], mouse_coords[1] + self.mouse_offset[1])
        # self.polygon_surface.fill((0, 0, 0, 255))

    def draw(self, buffer:pygame.Surface, debug_mode:bool) -> None:
        if (debug_mode):
            ### Rays
            for i in range(len(self.endpoints)):
                pygame.draw.line(buffer, (255, 0, 0), self.position, self.endpoints[i])

            ### Mask
            if len(self.endpoints) > 2:
                pygame.draw.polygon(buffer, (255, 0, 0), self.endpoints, 1)

            for i in range(len(self.mouse_endpoints)):
                pygame.draw.line(buffer, (255, 255, 0), self.mouse_startpoints[i], self.mouse_endpoints[i])
            
            if (len(self.mouse_endpoints) > 0):
                pygame.draw.circle(buffer, (0, 0, 255), self.mouse_endpoints[self.min_dist_index], 2)

            for i in range(len(self.interrupt_points)):
                # pygame.draw.line(buffer, (0, 255, 255), self.start_interrupt_points[i], self.interrupt_points[i], 2)
                pygame.draw.circle(buffer, (0, 255, 255), self.interrupt_points[i], 1)

        buffer.blit(
            self.texture,
            (self.position[0] - self.texture.get_width()//2, self.position[1] - self.texture.get_height()//2)
        )


        if (debug_mode):
            ### Center
            pygame.draw.circle(buffer, (0,0,255), self.position, 1, 1)

            ### Hitbox
            pygame.draw.circle(
                surface=buffer,
                color=(0, 0, 255),
                center=self.position,
                radius=self.texture.get_width()//4,
                width=1
            )

            ### Overlap stuff
            pygame.draw.line(buffer, (0, 0, 255), self.position, self.position - self.offset, 2)
            buffer.blit(source=self.overlap_mask.to_surface(setcolor=(50, 50, 50), unsetcolor=None), dest=(self.position[0] - self.texture.get_width()//2, self.position[1] - self.texture.get_height()//2))
            if(self.overlap_vector != None): pygame.draw.circle(buffer, (0, 255, 255), self.overlap_vector, 3)

