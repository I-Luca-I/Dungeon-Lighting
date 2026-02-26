import pygame, json, os, datetime, math
from . import pawn, mask, triggerables, time

class Game:
    def __init__(self, id:str, save:str, entrance:str) -> None:
        self.id = id
        self.save = save
        self.entrance = entrance

        ### Load local data
        dungeon_img = pygame.image.load(f"saves/dungeon_{self.id}/dungeon_{self.id}.png")
        triggerables_img = pygame.image.load(f"saves/dungeon_{self.id}/triggerables_{self.id}.png")
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
        cursor_stairs_img = pygame.image.load("assets/cursor_stairs.png")
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
        self.chase_mode = bool(self.settings["chase_mode"])
        self.dm_mode = False
        self.stairs_destinations = self.settings["stairs_destinations"]
        pygame.display.set_caption("Dungeon//Lighting")
        pygame.display.set_icon(icon)

        ### Game setup
        cursor_normal_img = pygame.transform.rotozoom(cursor_normal_img, 315, 100/cursor_normal_img.get_width())
        cursor_interact_img = pygame.transform.rotozoom(cursor_interact_img, 315, 100/cursor_interact_img.get_width())
        self.cursors = {
            "normal": pygame.cursors.Cursor((7, 28), cursor_normal_img),
            "interact": pygame.cursors.Cursor((7, 28), cursor_interact_img),
            "door": pygame.cursors.Cursor((7, 28), cursor_door_open_img),
            "close_door": pygame.cursors.Cursor((7, 28), cursor_door_close_img),
            "stairs": pygame.cursors.Cursor((7, 28), cursor_stairs_img)
        }
        pygame.mouse.set_cursor(self.cursors["normal"])

        self.party = pawn.Pawn(
            position=self.settings["party_position"] if(self.entrance == None) else self.settings["entrances"][self.entrance],
            radius=self.settings["party_radius"],
            img=pygame.image.load("assets/token.png"),
            size=float(self.settings["party_size"]),
        )

        ### DM mode setup
        self.add_light_in_mouse_pos = False
        ### keyboard repeat inputs
        pygame.key.set_repeat(10, 10)

        ### Camera
        self.zoom_exponent = int(self.settings["zoom_exponent"])
        self.zoom_factor = 1.1 ** self.zoom_exponent
        self.last_zoom_factor = self.zoom_factor
        self.scrolling = False
        self.camera_offset = pygame.Vector2(self.settings["camera_offset"])
        self.camera_view = pygame.Surface(size=(pygame.Vector2(pygame.display.get_window_size()))*(1//self.zoom_factor))

        ### Surfaces
        self.dungeon = pygame.surface.Surface(size=(dungeon_img.get_width(), dungeon_img.get_height()))
        self.dungeon.blit(dungeon_img, (0, 0))
        self.triggerables_surface = triggerables_img
        self.frame = pygame.surface.Surface(size=(frame_img.get_width(), frame_img.get_height()), flags=pygame.SRCALPHA)
        self.frame.blit(pygame.transform.rotozoom(frame_img, 0, info.current_w/frame_img.get_width()), (0, 0))

        ### Masks
        self.collision_mask = mask.Masks.get_collision_mask(self.dungeon, pygame.Color(0, 0, 35))
        shadow_surface = pygame.surface.Surface(size=self.dungeon.get_size())
        shadow_surface.blit(shadow_mask_img, (0, 0))
        self.shadow_mask = pygame.mask.from_threshold(surface=shadow_surface, color=(255, 255, 255), threshold=(1, 1, 1))
        self.light_mask = pygame.mask.Mask(size=(self.party.radius*2, self.party.radius*2), fill=False)

        self.door_mask = triggerables.Door.get_door_mask(self.triggerables_surface)
        self.doors = triggerables.Door.get_doors(self.door_mask)

        self.stairs_mask = triggerables.Stairs.get_stairs_mask(self.triggerables_surface)
        self.stairs = triggerables.Stairs.get_stairs(self.stairs_mask)

        self.dungeon_changers_mask = triggerables.DungeonChanger.get_changers_mask(self.triggerables_surface)
        self.dungeon_changers = triggerables.DungeonChanger.get_dungeon_changers(self.dungeon_changers_mask, self.settings["dungeon_changers_data"])
    
    def run(self) -> None:
        self.new_game_data = None
        timer = time.timer()
        while self.running:
            timer.reset()
            self.mouse_coords = (pygame.mouse.get_pos() - self.camera_offset) // self.zoom_factor

            self.event_loop()
            self.clock.tick(60)
            timer.add_breakpoint("event_loop")
            
            if (pygame.display.get_surface().get_width() > self.dungeon.get_width()*self.zoom_factor or pygame.display.get_surface().get_height() > self.dungeon.get_height()*self.zoom_factor):
                self.zoom_exponent += 1
                self.last_zoom_factor = self.zoom_factor
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

            mask.Masks.update_light(self.light_mask, self.party)
            timer.add_breakpoint("light_upd")

            mask.Masks.draw_light(buffer, self.shadow_mask, self.light_mask, self.party, self.chase_mode)
            timer.add_breakpoint("light_drw")

            self.party.draw(buffer, self.debug_mode)
            timer.add_breakpoint("party_drw")

            if (self.add_light_in_mouse_pos):
                self.add_light_in_mouse_pos = False
                instant_light = pawn.Pawn(position=pygame.Vector2(pygame.mouse.get_pos())//self.zoom_factor - self.camera_offset//self.zoom_factor, radius=30, img=pygame.Surface(size=(1,1)), size=1)
                instant_light.update(self.collision_mask)
                instant_light.draw(buffer, self.debug_mode)
                instant_light_mask = pygame.mask.Mask(size=(instant_light.radius*2, instant_light.radius*2), fill=False)
                mask.Masks.update_light(instant_light_mask, instant_light)
                mask.Masks.draw_light(buffer, self.shadow_mask, instant_light_mask, instant_light, self.chase_mode)

            if (self.debug_mode):
                for door in self.doors:
                    if door.states["is_open"]:
                        buffer.blit(source=door.masks["main_mask"].to_surface(setcolor=(0, 255, 255), unsetcolor=None), dest=door.coord)
                    else:
                        buffer.blit(source=door.masks["main_mask"].to_surface(setcolor=(0, 0, 255), unsetcolor=None), dest=door.coord)
                for stairs in self.stairs:
                    buffer.blit(source=stairs.masks["main_mask"].to_surface(setcolor=(255, 128, 0), unsetcolor=None), dest=stairs.coord)

                pygame.draw.line(buffer, (0, 255, 0), self.party.position, self.mouse_coords)
                
                versore_perpendicolare = pygame.Vector2(1,1)
                if (math.sqrt((self.mouse_coords[0]-self.party.position[0])**2+(self.mouse_coords[1]-self.party.position[1])**2)) != 0:
                    versore_perpendicolare = pygame.Vector2(-(self.mouse_coords[1]-self.party.position[1]), (self.mouse_coords[0]-self.party.position[0]))*(1/(math.sqrt((self.mouse_coords[0]-self.party.position[0])**2+(self.mouse_coords[1]-self.party.position[1])**2)))
                semibase = 4
                for i in range(semibase):
                    pygame.draw.line(buffer, (0, 255, 0, 255), self.party.position + versore_perpendicolare * i, self.mouse_coords + versore_perpendicolare * i)
                    pygame.draw.line(buffer, (0, 255, 0, 255), self.party.position - versore_perpendicolare * i, self.mouse_coords - versore_perpendicolare * i)
                
                pygame.draw.circle(buffer, (0, 255, 0), self.mouse_coords, 1, 1)

            ### Print buffer and frame on screen
            screen = pygame.display.get_surface()
            self.camera_view = pygame.Surface(size=(pygame.Vector2(pygame.display.get_window_size())) * (1 / self.zoom_factor))
            self.camera_view.blit(source=buffer, dest=((self.camera_offset)/self.zoom_factor))
            screen.blit(
               source=pygame.transform.scale_by(surface=self.camera_view, factor=self.zoom_factor),    #pygame.transform.scale_by(surface=buffer, factor=self.zoom_factor), # SLOOOOOW
               dest=(0, 0)                                                                             #self.camera_offset
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
        return self.new_game_data

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
            if pygame.mouse.get_pressed()[0] and not self.party.moving and not self.dm_mode:
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
            if triggerables.Door.check_click(self.door_mask, self.shadow_mask, self.mouse_coords) and not self.party.moving:
                ### finding closest door
                closest_door = self.doors[0]
                smaller_distance = abs(self.mouse_coords[0] - closest_door.coord[0]) + abs(self.mouse_coords[1] - closest_door.coord[1])
                for adoor in self.doors:
                    if smaller_distance == 0 or abs(self.mouse_coords[0] - adoor.coord[0]) + abs(self.mouse_coords[1] - adoor.coord[1]) < smaller_distance:
                        smaller_distance = abs(self.mouse_coords[0] - adoor.coord[0]) + abs(self.mouse_coords[1] - adoor.coord[1])
                        closest_door = adoor

                ### door cursor state
                cursor = self.cursors["door"] if not(closest_door.states["is_open"]) else self.cursors["close_door"]
                pygame.mouse.set_cursor(cursor)
                ### door trigger
                if pygame.mouse.get_pressed()[0]:
                    closest_door.trigger(self.collision_mask)

            ### Stairs interaction
            if triggerables.Stairs.check_click(self.stairs_mask, self.shadow_mask, self.mouse_coords) and triggerables.Stairs.check_click(self.stairs_mask, self.shadow_mask, self.party.position) and not self.party.moving:
                ### finding closest stairs
                closest_stairs = self.stairs[0]
                smaller_distance = abs(self.mouse_coords[0] - closest_stairs.coord[0]) + abs(self.mouse_coords[1] - closest_stairs.coord[1])
                for stairs in self.stairs:
                    if smaller_distance == 0 or abs(self.mouse_coords[0] - stairs.coord[0]) + abs(self.mouse_coords[1] - stairs.coord[1]) < smaller_distance:
                        smaller_distance = abs(self.mouse_coords[0] - stairs.coord[0]) + abs(self.mouse_coords[1] - stairs.coord[1])
                        closest_stairs = stairs
                ### stairs cursor state
                cursor = self.cursors["stairs"]
                pygame.mouse.set_cursor(cursor)
                ### stairs trigger
                if pygame.mouse.get_pressed()[0]:
                    self.move_camera(closest_stairs.trigger(self.stairs, self.stairs_destinations))
                    self.party.position = closest_stairs.trigger(self.stairs, self.stairs_destinations)

            ### DungeonChanger interaction
            if triggerables.DungeonChanger.check_click(self.dungeon_changers_mask, self.shadow_mask, self.mouse_coords) and not self.party.moving:
                ### finding closest dungeon changer
                closest_dungeon_changers = self.dungeon_changers[0]
                smaller_distance = abs(self.mouse_coords[0] - closest_dungeon_changers.coord[0]) + abs(self.mouse_coords[1] - closest_dungeon_changers.coord[1])
                for dungeon_changer in self.dungeon_changers:
                    if smaller_distance == 0 or abs(self.mouse_coords[0] - dungeon_changer.coord[0]) + abs(self.mouse_coords[1] - dungeon_changer.coord[1]) < smaller_distance:
                        smaller_distance = abs(self.mouse_coords[0] - dungeon_changer.coord[0]) + abs(self.mouse_coords[1] - dungeon_changer.coord[1])
                        closest_dungeon_changers = dungeon_changer
                ### dungeon_changer cursor state
                cursor = self.cursors[closest_dungeon_changers.states["cursor"]]
                pygame.mouse.set_cursor(cursor)
                ### dungeon_changer trigger
                if pygame.mouse.get_pressed()[0]:
                    self.new_game_data = closest_dungeon_changers.trigger()
                    self.running = False

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

                ### Chase mode
                if event.key == pygame.K_c:
                    self.chase_mode = not self.chase_mode

                ### DM mode

                keys = pygame.key.get_pressed()
                if keys[pygame.K_d]:
                    self.dm_mode = True
                    ### Add instant light source
                    if pygame.mouse.get_pressed()[0] and not self.party.moving:
                        self.add_light_in_mouse_pos = True
                else:
                    self.dm_mode = False

            ### Zoom (REDO)
            if event.type == pygame.MOUSEWHEEL:
                if (event.y > 0):
                    self.zoom_exponent += 1

                else:
                    self.zoom_exponent -= 1
                self.last_zoom_factor = self.zoom_factor
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
            "debug_mode": self.debug_mode,
            "chase_mode": self.chase_mode,
            "stairs_destinations": self.stairs_destinations,
            "entrances":self.settings["entrances"],
            "dungeon_changers_data":self.settings["dungeon_changers_data"]
        }

        os.makedirs(f"saves/dungeon_{id}", exist_ok=True)
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        
        with open(f"saves/dungeon_{id}/{date}_config.json", "w") as file:
            json.dump(settings, file, indent=0)

        save_surface = self.shadow_mask.to_surface()
        pygame.image.save(save_surface, f"saves/dungeon_{id}/{date}_light_mask.png")

    def quit(self) -> None:
        self.save_dungeon(self.id)
        pygame.quit()
