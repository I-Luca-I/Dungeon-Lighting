import pygame, json, os, datetime
from . import pawn, mask, door, time

class Game:
    def __init__(self, id:str, save:str) -> None:
        self.id = id
        self.save = save

        ### Load local data
        dungeon_img = pygame.image.load(f"saves/dungeon_{self.id}/dungeon_{self.id}.png")
        doors_img = pygame.image.load(f"saves/dungeon_{self.id}/doors_{self.id}.png")
        try:
            shadow_mask_img = pygame.image.load(f"saves/dungeon_{self.id}/{self.save}_light_mask.png")
        except:
            shadow_mask_img = pygame.surface.Surface(size=dungeon_img.get_size())
            shadow_mask_img.fill(color=(0, 0, 0))
        with open(f"saves/dungeon_{self.id}/{self.save}_config.json", "r") as file:
            self.settings = json.load(file)
         
        ### Load absolute data
        cursor_normal_img = pygame.image.load("assets/cursor_normal.png")
        cursor_interact_img = pygame.image.load("assets/cursor_interact.png")
        cursor_door_open_img = pygame.image.load("assets/cursor_door_closed.png")
        cursor_door_close_img = pygame.image.load("assets/cursor_door_open.png")
        frame_img = pygame.image.load("assets/frame.png")
        icon = pygame.image.load("assets/icon.ico")
        
        ### Pygame setup
        info = pygame.display.Info()
        pygame.display.set_mode(
            size=(info.current_w, info.current_h)
        )
        self.clock = pygame.time.Clock()
        self.running = True
        self.debug_mode = bool(self.settings["debug_mode"])
        pygame.display.set_caption("Dungeon//Lighting")
        pygame.display.set_icon(icon)

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
        self.frame.blit(pygame.transform.rotozoom(frame_img, 0, info.current_w/frame_img.get_width()), (0, 0))

        ### Masks
        self.collision_mask = mask.Masks.get_collision_mask(self.dungeon, pygame.Color(0, 0, 35))
        shadow_surface = pygame.surface.Surface(size=self.dungeon.get_size())
        shadow_surface.blit(shadow_mask_img, (0, 0))
        self.shadow_mask = pygame.mask.from_threshold(surface=shadow_surface, color=(255, 255, 255), threshold=(1, 1, 1))
        self.light_mask = pygame.mask.Mask(size=(self.party.radius*2, self.party.radius*2), fill=False)
        self.door_mask = door.Door.get_door_mask(self.door_surface)
        self.doors = door.Door.get_doors(self.door_mask)
    
    def run(self) -> None:
        timer = time.timer()
        while self.running:
            timer.reset()
            self.mouse_coords = (pygame.mouse.get_pos() - self.camera_offset) // self.zoom_factor

            self.event_loop()
            self.clock.tick(60)
            timer.add_breakpoint("event_loop")
            
            if (pygame.display.get_surface().get_width() > self.dungeon.get_width()*self.zoom_factor or pygame.display.get_surface().get_height() > self.dungeon.get_height()*self.zoom_factor):
                self.zoom_exponent += 1
                self.zoom_factor = 1.1 ** self.zoom_exponent
            self.camera_offset[0] = min(0, max(self.camera_offset[0], pygame.display.get_surface().get_width()-self.dungeon.get_width()*self.zoom_factor))
            self.camera_offset[1] = min(0, max(self.camera_offset[1], pygame.display.get_surface().get_height()-self.dungeon.get_height()*self.zoom_factor))

            buffer = pygame.surface.Surface(size=(self.dungeon.get_width(), self.dungeon.get_height()), flags=pygame.SRCALPHA)
            buffer.blit(source=self.dungeon, dest=(0, 0))

            if (self.debug_mode):
                buffer.blit(source=self.collision_mask.to_surface(setcolor=(0, 255, 0), unsetcolor=(255, 255, 255)), dest=(0, 0))
            timer.add_breakpoint("pre_updates")

            self.party.update(self.collision_mask)
            timer.add_breakpoint("party_upd")

            mask.Masks.update_light(self.shadow_mask, self.light_mask, self.party)
            timer.add_breakpoint("light_upd")

            mask.Masks.draw_light(buffer, self.shadow_mask, self.light_mask, self.party)
            timer.add_breakpoint("light_drw")

            self.party.draw(buffer, self.debug_mode)
            timer.add_breakpoint("party_drw")

            if (self.debug_mode):
                for door in self.doors:
                    if door.is_open:
                        buffer.blit(source=door.mask.to_surface(setcolor=(0, 255, 255), unsetcolor=None), dest=door.coord)
                    else:
                        buffer.blit(source=door.mask.to_surface(setcolor=(0, 0, 255), unsetcolor=None), dest=door.coord)

                pygame.draw.line(buffer, (0, 255, 0), self.party.position, self.mouse_coords)
                pygame.draw.circle(buffer, (0, 255, 0), self.mouse_coords, 1, 1)

            ### Print buffer and frame on screen
            screen = pygame.display.get_surface()
            screen.blit(
                source=pygame.transform.scale_by(surface=buffer, factor=self.zoom_factor), # SLOOOOOW
                # source=buffer,
                dest=self.camera_offset
            )
            screen.blit(source=self.frame, dest=(0, 0))

            pygame.display.flip()
            timer.add_breakpoint("buffer+frame_drw")

            print(f"Times: {timer.mid_printable}")
            print("\033[1A", end="")

            if (self.debug_mode):
                print(f"FPS: {self.clock.get_fps()}")
                print(f"Mouse coords: {self.mouse_coords}")
                print(f"Party position: {self.party.position}")
                print(f"Camera offset: {self.camera_offset}")
                print("\033[4A", end="")

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
                    self.previous_mouse_pos = pygame.mouse.get_pos()
                    self.previous_camera_offset = self.camera_offset
                else:
                    self.camera_offset = self.previous_camera_offset + pygame.mouse.get_pos() - self.previous_mouse_pos
                    self.previous_camera_offset = self.camera_offset
                    self.previous_mouse_pos = pygame.mouse.get_pos()
            else:
                self.scrolling = False

            ### Door interaction
            if door.Door.check_door_click(self.door_mask, self.shadow_mask, self.mouse_coords) and not self.party.moving:
                ### finding closest door
                closest_door = self.doors[0]
                smaller_distance = abs(self.mouse_coords[0] - closest_door.coord[0]) + abs(self.mouse_coords[1] - closest_door.coord[1])
                for adoor in self.doors:
                    if smaller_distance == 0 or abs(self.mouse_coords[0] - adoor.coord[0]) + abs(self.mouse_coords[1] - adoor.coord[1]) < smaller_distance:
                        smaller_distance = abs(self.mouse_coords[0] - adoor.coord[0]) + abs(self.mouse_coords[1] - adoor.coord[1])
                        closest_door = adoor
                ### door cursor state
                cursor = self.cursors["open_door"] if not(closest_door.is_open) else self.cursors["close_door"]
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

        save_surface = self.shadow_mask.to_surface()
        pygame.image.save(save_surface, f"saves/dungeon_{id}/{date}_light_mask.png")

    def quit(self) -> None:
        self.save_dungeon(self.id)
        pygame.quit()
