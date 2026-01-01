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

        ### Game setup
        self.zoom_factor = 1.1 ** float(settings["zoom_exponent"])

        cursor_normal_img = pygame.transform.rotozoom(cursor_normal_img, 315, 100/cursor_normal_img.get_width())
        cursor_interact_img = pygame.transform.rotozoom(cursor_interact_img, 315, 100/cursor_interact_img.get_width())
        self.cursors = {
            "normal": pygame.cursors.Cursor((10, 40), cursor_normal_img),
            "interact": pygame.cursors.Cursor((10, 40), cursor_interact_img)
        }
        pygame.mouse.set_cursor(self.cursors["normal"])

        # REDO
        self.party = pawn.Pawn(
            position=[int(int(settings["starting_coords"][0])*self.zoom_factor), int(int(settings["starting_coords"][1])*self.zoom_factor)], 
            radius=100,
            img="assets/token.png",
            size=float(settings["token_relative_size"]),
            zoom_factor=self.zoom_factor
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
        self.dungeon = pygame.transform.rotozoom(surface=self.dungeon, angle=0, scale=self.zoom_factor)
        self.doors = pygame.transform.rotozoom(surface=doors_img, angle=0, scale=self.zoom_factor)

        ### Masks (REDO)
        self.collision_mask = mask.get_collision_mask(self.dungeon, {"b":35, "r":0})
        door_mask = mask.get_door_mask(self.doors)
        self.doors = mask.get_doors(self.doors, door_mask)
    
    def run(self):
        while self.running:
            self.event_loop()
            
            self.clock.tick(60)
            # print(f"\rFPS: {self.clock.get_fps()}", end="")

            screen = pygame.display.get_surface()

            ### REDO REDO REDO
            self.party.update(self.temp_surf, self.dungeon, self.collision_mask, self.camera_offset)
            mask.get_shadow(self.temp_surf, self.dungeon, self.camera_offset, (self.party.position[0] - self.camera_offset[0], self.party.position[1] - self.camera_offset[1]), self.party.radius, self.party)
            screen.blit(self.temp_surf, (0, 0))
            self.party.draw(screen, self.camera_offset)
            mask.reset_shadow((self.party.position[0] - self.camera_offset[0], self.party.position[1] - self.camera_offset[1]), self.party.radius)
            # screen.blit(door_test_surf, self.camera_offset)

            pygame.display.flip()

        self.quit()

    def event_loop(self):
        for event in pygame.event.get():
            ### Quit
            if event.type == pygame.QUIT:
                self.running = False
            
            ### Update cursor
            if pygame.mouse.get_pressed()[0]:
                pygame.mouse.set_cursor(self.cursors["interact"])
            else:
                pygame.mouse.set_cursor(self.cursors["normal"])

            if event.type == pygame.KEYDOWN:
                ### Center to party (REDO)
                if event.key == pygame.K_t:
                    self.party.center_to_camera(pygame.display.get_surface(), self.camera_offset)
                
                ### Manual save
                if event.key == pygame.K_s:
                    self.save()

            ### self.Party movement (REDO)
            if (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 
                (self.party.position[0] - self.party.texture.get_width() // 2) < pygame.mouse.get_pos()[0] < (self.party.position[0] + self.party.texture.get_width() // 2) and 
                (self.party.position[1] - self.party.texture.get_height() // 2) < pygame.mouse.get_pos()[1] < (self.party.position[1] + self.party.texture.get_height() // 2)
            ):
                self.party.moving = True
                self.party.mouse_offset = [self.party.position[0] - pygame.mouse.get_pos()[0], self.party.position[1] - pygame.mouse.get_pos()[1]]
            elif (
                event.type == pygame.MOUSEBUTTONUP and event.button == 1
            ):
                self.party.moving = False

            if self.party.moving:
                if (self.party.update_collision(self.collision_mask, (pygame.mouse.get_pos()[0] - self.party.hitbox_surface.get_width() // 2 - self.camera_offset[0], pygame.mouse.get_pos()[1] - self.party.hitbox_surface.get_height() // 2 - self.camera_offset[1]))) < 50:
                    self.party.position = (pygame.mouse.get_pos()[0] + self.party.mouse_offset[0], pygame.mouse.get_pos()[1] + self.party.mouse_offset[1])
            
            ### Screen scrolling (REDO)
            if pygame.mouse.get_pressed()[0] and not self.party.moving:
                if not self.scrolling:
                    self.scrolling = not self.scrolling
                    self.last_offset = self.camera_offset
                    self.last_pos = pygame.mouse.get_pos()
                    self.last_c_pos = self.party.position
                else:
                    self.camera_offset = [self.last_offset[0] + (pygame.mouse.get_pos()[0] - self.last_pos[0]), self.last_offset[1] + (pygame.mouse.get_pos()[1] - self.last_pos[1])]
                    self.party.position = [self.last_c_pos[0] + (pygame.mouse.get_pos()[0] - self.last_pos[0]), self.last_c_pos[1] + (pygame.mouse.get_pos()[1] - self.last_pos[1])]
            else:
                self.scrolling = 0

            ### DOOR CHECK (TEST)
            # if pygame.mouse.get_pressed()[0] and mask.check_door_click(door_mask, (pygame.mouse.get_pos()[0] - camera_offset[0], pygame.mouse.get_pos()[1] - camera_offset[1])):
            #     print("!")

    def save(self):
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
