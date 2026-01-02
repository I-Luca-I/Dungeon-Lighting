import pygame, json
from . import pawn, mask

class Game:
    def __init__(self):
        ### Load data
        with open("config/default.json", "r") as file:
            settings = json.load(file)
        cursor_normal_img = pygame.image.load("assets/cursor_normal.png")
        cursor_interact_img = pygame.image.load("assets/cursor_interact.png")
        dungeon_img = pygame.image.load("assets/local/dungeon.png")
        doors_img = pygame.image.load("assets/local/doors.png")

        ### Pygame setup
        pygame.display.set_mode(
            size=(500, 500)
        )
        self.clock = pygame.time.Clock()
        self.running = True
        self.debug_mode = True

        ### Game setup
        self.zoom_exponent = settings["zoom_exponent"]
        self.zoom_factor = 1.1 ** self.zoom_exponent

        cursor_normal_img = pygame.transform.rotozoom(cursor_normal_img, 315, 100/cursor_normal_img.get_width())
        cursor_interact_img = pygame.transform.rotozoom(cursor_interact_img, 315, 100/cursor_interact_img.get_width())
        self.cursors = {
            "normal": pygame.cursors.Cursor((10, 40), cursor_normal_img),
            "interact": pygame.cursors.Cursor((10, 40), cursor_interact_img)
        }
        pygame.mouse.set_cursor(self.cursors["normal"])

        self.party = pawn.Pawn(
            position=settings["starting_coords"],
            radius=100,
            img=pygame.image.load("assets/token.png"),
            size=float(settings["token_relative_size"]),
        )

        self.scrolling = False
        self.camera_offset = [0, 0]
        self.save_num = settings["save_number"]

        ### Surfaces (REDO)
        self.temp_surf = pygame.surface.Surface(size=(dungeon_img.get_width(), dungeon_img.get_height()))  # serve usare una superfice ulteriore per salvare la shadow al posto dello screen, per permettere il movimento della visuale senza rompere tutto
        self.temp_surf.fill((255, 255, 255, 0))
        self.temp_surf = pygame.transform.rotozoom(self.temp_surf, 0, self.zoom_factor)
        self.dungeon = pygame.surface.Surface(size=(dungeon_img.get_width(), dungeon_img.get_height()))
        self.dungeon.blit(dungeon_img, (0, 0))
        # self.dungeon = pygame.transform.rotozoom(surface=self.dungeon, angle=0, scale=self.zoom_factor)
        self.doors = pygame.transform.rotozoom(surface=doors_img, angle=0, scale=self.zoom_factor)

        ### Masks (REDO)
        self.collision_mask = mask.get_collision_mask(self.dungeon, {"b":35, "r":0})
        door_mask = mask.get_door_mask(self.doors)
        self.doors = mask.get_doors(self.doors, door_mask)
    
    def run(self):
        while self.running:
            self.mouse_coords = [(pygame.mouse.get_pos()[0] - self.camera_offset[0])//self.zoom_factor, (pygame.mouse.get_pos()[1] - self.camera_offset[1])//self.zoom_factor]

            self.event_loop()
            self.clock.tick(60)
            
            self.zoom_factor = 1.1 ** self.zoom_exponent

            buffer = pygame.surface.Surface(size=(self.dungeon.get_width(), self.dungeon.get_height()))
            buffer.blit(source=self.dungeon, dest=(0, 0))

            if (self.debug_mode):
                print(f"FPS: {self.clock.get_fps()}")
                print(f"Mouse coords: {self.mouse_coords}")
                print(f"Party position: {self.party.position}")
                print(f"Camera offset: {self.camera_offset}")
                print("\033[4A", end="")

                buffer.blit(source=self.collision_mask.to_surface(), dest=(0, 0))

            ### REDO REDO REDO
            self.party.update(self.collision_mask)    
            # mask.get_shadow(self.temp_surf, self.dungeon, self.camera_offset, (self.party.position[0] - self.camera_offset[0], self.party.position[1] - self.camera_offset[1]), self.party.radius, self.party)
            # screen.blit(self.temp_surf, (0, 0))
            self.party.draw(buffer, self.debug_mode)
            # mask.reset_shadow((self.party.position[0] - self.camera_offset[0], self.party.position[1] - self.camera_offset[1]), self.party.radius)
            
            if (self.debug_mode):
                pygame.draw.circle(buffer, (0,255,0), self.mouse_coords, 1, 1)

            screen = pygame.display.get_surface()
            screen.blit(
                source=pygame.transform.rotozoom(surface=buffer, angle=0, scale=self.zoom_factor),
                dest=self.camera_offset
            )

            pygame.display.flip()

        self.quit()

    def event_loop(self):
        for event in pygame.event.get():
            self.party.move(event, self.mouse_coords, self.collision_mask)

            ### Quit
            if event.type == pygame.QUIT:
                self.running = False
            
            ### Update cursor
            if pygame.mouse.get_pressed()[0]:
                pygame.mouse.set_cursor(self.cursors["interact"])
            else:
                pygame.mouse.set_cursor(self.cursors["normal"])

            ### Screen scrolling
            if pygame.mouse.get_pressed()[0] and not self.party.moving:
                if not self.scrolling:
                    self.scrolling = True
                    self.start_mouse_pos = pygame.mouse.get_pos()
                    self.start_camera_offset = self.camera_offset
                else:
                    self.camera_offset = [self.start_camera_offset[0] + pygame.mouse.get_pos()[0] - self.start_mouse_pos[0], self.start_camera_offset[1] + pygame.mouse.get_pos()[1] - self.start_mouse_pos[1]]
            else:
                self.scrolling = False

            if event.type == pygame.KEYDOWN:
                ### Center to party
                if event.key == pygame.K_t:
                    self.move_camera(self.party.position)
                    self.party.moving = False
                
                ### Manual save
                if event.key == pygame.K_s:
                    self.save()
                
                ### Debug mode
                if event.key == pygame.K_F4:
                    self.debug_mode = not self.debug_mode

            ### Zoom
            if event.type == pygame.MOUSEWHEEL:
                if (event.y > 0):
                    self.zoom_exponent += 1
                else:
                    self.zoom_exponent -= 1

    def move_camera(self, coords:list[int]):
        self.camera_offset[0] = pygame.display.get_surface().get_width()//2 - coords[0]*self.zoom_factor
        self.camera_offset[1] = pygame.display.get_surface().get_height()//2 - coords[1]*self.zoom_factor

    def save(self): ### REDO REDO REDO
        self.save_num += 1
        with open("config/default.json", "r") as file:
            settings = json.load(file)

        settings = {
            "zoom_exponent": settings["zoom_exponent"],
            "token_relative_size": settings["token_relative_size"],
            "starting_coords": settings["starting_coords"],
            "save_number": self.save_num
        }

        with open("config/default.json", "w") as file:
            json.dump(settings, file)
        
        save_surf = mask.get_save_surface(self.dungeon.convert_alpha())
        pygame.image.save(save_surf, f"saves/save_{self.save_num}.png")

    def quit(self):
        self.save()
        pygame.quit()
