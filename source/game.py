import pygame, json, os, datetime
from . import pawn, mask, door

class Game:
    def __init__(self, id:str, save:str) -> None:
        self.id = id
        self.save = save

        ### Load local data
        dungeon_img = pygame.image.load(f"assets/local/dungeon_{self.id}.png")
        doors_img = pygame.image.load(f"assets/local/doors_{self.id}.png")
        light_mask_img = pygame.image.load(f"saves/dungeon_{self.id}/{self.save}_light_mask.png")
        with open(f"saves/dungeon_{self.id}/{self.save}_config.json", "r") as file:
            self.settings = json.load(file)
         
        ### Load absolute data
        cursor_normal_img = pygame.image.load("assets/cursor_normal.png")
        cursor_interact_img = pygame.image.load("assets/cursor_interact.png")
        cursor_door_open_img = pygame.image.load("assets/cursor_door_closed.png")
        cursor_door_close_img = pygame.image.load("assets/cursor_door_open.png")
        frame_img = pygame.image.load("assets/frame.png")
        
        ### Pygame setup
        pygame.display.set_mode(
            size=(1920, 1080)
        )
        self.clock = pygame.time.Clock()
        self.running = True
        self.debug_mode = bool(self.settings["debug_mode"])

        ### Game setup
        cursor_normal_img = pygame.transform.rotozoom(cursor_normal_img, 315, 100/cursor_normal_img.get_width())
        cursor_interact_img = pygame.transform.rotozoom(cursor_interact_img, 315, 100/cursor_interact_img.get_width())
        self.cursors = {
            "normal": pygame.cursors.Cursor((7, 28), cursor_normal_img),
            "interact": pygame.cursors.Cursor((7, 28), cursor_interact_img),
            "open_door": pygame.cursors.Cursor((0, 0), cursor_door_open_img),
            "close_door": pygame.cursors.Cursor((0, 0), cursor_door_close_img)
        }
        pygame.mouse.set_cursor(self.cursors["normal"])

        self.party = pawn.Pawn(
            position=self.settings["party_position"],
            radius=self.settings["party_radius"],
            img=pygame.image.load("assets/token.png"),
            size=float(self.settings["party_size"]),
        )

        ### Camera
        self.zoom_exponent = int(self.settings["zoom_exponent"])
        self.zoom_factor = 1.1 ** self.zoom_exponent
        self.scrolling = False
        self.camera_offset = pygame.Vector2(self.settings["camera_offset"])

        ### Surfaces
        self.dungeon = pygame.surface.Surface(size=(dungeon_img.get_width(), dungeon_img.get_height()))
        self.dungeon.blit(dungeon_img, (0, 0))
        self.door_surface = doors_img
        self.frame = pygame.surface.Surface(size=(frame_img.get_width(), frame_img.get_height()), flags=pygame.SRCALPHA)
        # frame_img.convert_alpha()
        self.frame.blit(frame_img, (0, 0))

        ### Masks
        self.collision_mask = mask.Masks.get_collision_mask(self.dungeon, pygame.Color(0, 0, 35))
        if (self.save == "0000-00-00"):
            self.light_mask = pygame.mask.Mask(size=self.dungeon.get_size(), fill=False)
        else:
            light_surface = pygame.surface.Surface(size=self.dungeon.get_size())
            light_surface.blit(light_mask_img, (0, 0))
            self.light_mask = pygame.mask.from_threshold(surface=light_surface, color=(255, 255, 255), threshold=(1, 1, 1))
        self.door_mask = door.Door.get_door_mask(self.door_surface)
        self.doors = door.Door.get_doors(self.door_mask)
    
    def run(self) -> None:
        while self.running:
            self.mouse_coords = (pygame.mouse.get_pos() - self.camera_offset) // self.zoom_factor

            self.event_loop()
            self.clock.tick(60)
            
            if (pygame.display.get_surface().get_width() > self.dungeon.get_width()*self.zoom_factor or pygame.display.get_surface().get_height() > self.dungeon.get_height()*self.zoom_factor):
                self.zoom_exponent += 1
                self.zoom_factor = 1.1 ** self.zoom_exponent
            self.camera_offset[0] = min(0, max(self.camera_offset[0], pygame.display.get_surface().get_width()-self.dungeon.get_width()*self.zoom_factor))
            self.camera_offset[1] = min(0, max(self.camera_offset[1], pygame.display.get_surface().get_height()-self.dungeon.get_height()*self.zoom_factor))

            buffer = pygame.surface.Surface(size=(self.dungeon.get_width(), self.dungeon.get_height()), flags=pygame.SRCALPHA)
            buffer.blit(source=self.dungeon, dest=(0, 0))

            if (self.debug_mode):
                print(f"FPS: {self.clock.get_fps()}")
                print(f"Mouse coords: {self.mouse_coords}")
                print(f"Party position: {self.party.position}")
                print(f"Camera offset: {self.camera_offset}")
                print("\033[4A", end="")

                buffer.blit(source=self.collision_mask.to_surface(setcolor=(0, 255, 0), unsetcolor=(255, 255, 255)), dest=(0, 0))

            self.party.update(self.collision_mask)
            mask.Masks.update_light(self.light_mask, self.party)
            mask.Masks.draw_light(buffer, self.light_mask, self.party)
            self.party.draw(buffer, self.debug_mode)

            if (self.debug_mode):
                pygame.draw.line(buffer, (0, 255, 0), self.party.position, self.mouse_coords)
                pygame.draw.circle(buffer, (0, 255, 0), self.mouse_coords, 1, 1)

            ### Print buffer on screen
            screen = pygame.display.get_surface()
            screen.blit(
                source=pygame.transform.rotozoom(surface=buffer, angle=0, scale=self.zoom_factor),
                dest=self.camera_offset
            )
            screen.blit(source=pygame.transform.rotozoom(surface=self.frame, angle=0, scale=1), dest=(0, 0))
            pygame.display.flip()

        self.quit()

    def event_loop(self) -> None:
        for event in pygame.event.get():
            self.party.handle_events(event, self.mouse_coords, self.collision_mask)

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
                    self.camera_offset = self.start_camera_offset + pygame.mouse.get_pos() - self.start_mouse_pos
            else:
                self.scrolling = False

            ### Door interaction
            if door.Door.check_door_click(self.door_mask, self.light_mask, self.mouse_coords) and not self.party.moving:
                ### finding closest door
                closest_door = self.doors[0]
                smaller_distance = abs(self.mouse_coords[0] - closest_door.coord[0]) + abs(self.mouse_coords[1] - closest_door.coord[1])
                for adoor in self.doors:
                    if smaller_distance == 0 or abs(self.mouse_coords[0] - adoor.coord[0]) + abs(self.mouse_coords[1] - adoor.coord[1]) < smaller_distance:
                        smaller_distance = abs(self.mouse_coords[0] - adoor.coord[0]) + abs(self.mouse_coords[1] - adoor.coord[1])
                        closest_door = adoor
                ### door cursor state
                cursor = self.cursors["open_door"] if closest_door.state == "closed" else self.cursors["close_door"]
                pygame.mouse.set_cursor(cursor)
                ### door trigger
                if pygame.mouse.get_pressed()[0]:
                    closest_door.trigger(self.collision_mask)

            if event.type == pygame.KEYDOWN:
                ### Center to party
                if event.key == pygame.K_t:
                    self.move_camera(self.party.position)
                    self.party.moving = False
                
                ### Manual save
                if event.key == pygame.K_s:
                    self.save_dungeon(self.id)
                
                ### Debug mode
                if event.key == pygame.K_F4:
                    self.debug_mode = not self.debug_mode

            ### Zoom (REDO)
            if event.type == pygame.MOUSEWHEEL:
                if (event.y > 0):
                    self.zoom_exponent += 1

                else:
                    self.zoom_exponent -= 1
                self.zoom_factor = 1.1 ** self.zoom_exponent
                self.move_camera(self.party.position)
                self.party.moving = False
                               
    def move_camera(self, coords:pygame.Vector2) -> None:
        self.camera_offset[0] = pygame.display.get_surface().get_width()//2 - coords[0]*self.zoom_factor
        self.camera_offset[1] = pygame.display.get_surface().get_height()//2 - coords[1]*self.zoom_factor

    def save_dungeon(self, id:str) -> None:
        settings = {
            "zoom_exponent": self.zoom_exponent,
            "party_size": self.settings["party_size"],
            "party_position": [self.party.position[0], self.party.position[1]],
            "party_radius": self.party.radius,
            "camera_offset": [self.camera_offset[0], self.camera_offset[1]],
            "debug_mode": self.debug_mode
        }

        os.makedirs(f"saves/dungeon_{id}", exist_ok=True)
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        
        with open(f"saves/dungeon_{id}/{date}_config.json", "w") as file:
            json.dump(settings, file)

        save_surface = self.light_mask.to_surface()
        pygame.image.save(save_surface, f"saves/dungeon_{id}/{date}_light_mask.png")

    def quit(self) -> None:
        self.save_dungeon(self.id)
        pygame.quit()
