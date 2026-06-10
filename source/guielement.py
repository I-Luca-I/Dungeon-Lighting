import pygame, math
from . import triggerables


class GUIElement(triggerables.Triggerable):
    def __init__(self, surfaces:dict[str:pygame.Surface, str:list[pygame.Surface]], masks:dict[str:pygame.Mask], coord:pygame.Vector2, draggable:bool, sub_elements=()):
        super(GUIElement, self).__init__(masks, coord, states={"being_dragged":False, "been_clicked":False, "draggable":draggable})
        self.current_mask:pygame.Mask = self.masks["default"]
        self.surfaces:dict[str:pygame.Surface, str:list[pygame.Surface]] = surfaces
        self.current_surface:pygame.Surface = self.surfaces["default"]
        self.sub_elements:tuple[GUIElement] = sub_elements
        self.frame_number = None
        self.trigger_switch = None

    def trigger(self):  # dato che per ora non abbiamo nessun altro trigger non faccio una classe apparte, se ci cerve un trigger diverso allora potremmo dividerli in due classi
        if self.frame_number == None:
            if self.trigger_switch == None:
                self.trigger_switch = False
            if self.trigger_switch:
                self.frame_number = len(self.surfaces["trigger_animation"])-1
                self.current_mask = self.masks["default"]
            else:
                self.frame_number = 0
                self.current_mask = self.masks["triggered"]

        if (self.frame_number == len(self.surfaces["trigger_animation"]) and not self.trigger_switch) or (self.frame_number == 0 and self.trigger_switch):
            self.trigger_switch = not self.trigger_switch
            self.states["been_clicked"] = False
            self.frame_number = None
            return

        self.current_surface = self.surfaces["trigger_animation"][self.frame_number]
        if self.trigger_switch:
            self.frame_number -= 1
        else:
            self.frame_number += 1


    def drag(self, mouse_coords:pygame.Vector2, mouse_offset:pygame.Vector2):
        self.coord = mouse_coords + mouse_offset

    def handle_events(self, mouse_coords:pygame.Vector2, event:pygame.event.Event = None):
        x, y = mouse_coords - self.coord
        if event != None:
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.states["draggable"] and 0 <= x <= self.current_surface.get_size()[0] and 0 <= y <= self.current_surface.get_size()[1] and not self.states["being_dragged"]):
                if self.current_mask.get_at((x,y)):
                    self.states["being_dragged"] = True
                    self.mouse_offset = self.coord - mouse_coords
            elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                self.states["being_dragged"] = False

            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3) and 0 <= x <= self.current_surface.get_size()[0] and 0 <= y <= self.current_surface.get_size()[1]:
                if self.current_mask.get_at((x, y)):
                    self.states["being_dragged"] = False
                    self.states["been_clicked"] = True

        if self.states["being_dragged"]:
            self.drag(mouse_coords, self.mouse_offset)
        if self.states["been_clicked"]:
            self.trigger()

    def draw(self, buffer:pygame.Surface):
        buffer.blit(self.current_surface, dest=self.coord)
        buffer.blit(self.current_mask.to_surface(setcolor=(255,0,0,120), unsetcolor=None), dest=self.coord)


    @staticmethod
    def make_GUIElements():
        GUIElements = []

        ### TOP POSTER ###
        surfaces = {"default": pygame.image.load("assets/top_poster.png"),
                    "trigger_animation": []}
        def_mask = pygame.Mask(size=pygame.image.load("assets/top_poster.png").get_size(), fill=True)
        trig_mask = def_mask.copy()
        trig_mask.erase(def_mask, offset=(0, int(pygame.image.load("assets/top_poster.png").get_size()[1] * 0.25)))
        masks = {"default": def_mask,
                 "triggered": trig_mask}
        top_poster = GUIElement(surfaces=surfaces, masks=masks, coord=pygame.Vector2((25,26)), draggable=False)
        GUIElements.append(top_poster)
        # animation #
        for i in range(30):
            surf = pygame.Surface(size=pygame.image.load("assets/top_poster.png").get_size(), flags=pygame.SRCALPHA)
            surf.fill((0,0,0,0))
            surf.blit(pygame.image.load("assets/top_poster.png"), dest=(0, math.ceil(0.8*pygame.image.load("assets/top_poster.png").get_size()[1]*((math.e**(-(0.1075331034*i))+math.sin(-10*(0.1075331034*i))*(math.e**(-(-(0.1075331034*i)+6.8))))-1))))
            surfaces["trigger_animation"].append(surf)


        ### TOP-RIGHT POSTER ###
        surfaces = {"default": pygame.image.load("assets/top_right_poster.png"),
                    "trigger_animation": []}
        def_mask = pygame.Mask(size=pygame.image.load("assets/top_right_poster.png").get_size(), fill=True)
        trig_mask = def_mask.copy()
        trig_mask.erase(def_mask, offset=(-int(pygame.image.load("assets/top_right_poster.png").get_size()[1] * 0.25), 0))
        masks = {"default": def_mask,
                 "triggered": trig_mask}
        top_right_poster = GUIElement(surfaces=surfaces, masks=masks, coord=pygame.Vector2((1619, 26)), draggable=False)
        GUIElements.append(top_right_poster)
        # animation #
        for i in range(30):
            surf = pygame.Surface(size=pygame.image.load("assets/top_right_poster.png").get_size(), flags=pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            surf.blit(pygame.image.load("assets/top_right_poster.png"), dest=(int(0.8 * pygame.image.load("assets/top_right_poster.png").get_size()[1] * math.e**(-0.3464955555*i)-1), 0))
            surfaces["trigger_animation"].append(surf)


        return GUIElements
