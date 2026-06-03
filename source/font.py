import pygame

class Font:
    def __init__(self, path:str) -> None:
        self.chars:list[pygame.Surface] = []
        font = pygame.image.load(path)
        for i in range(87):
            if 26 <= i < 62:
                self.chars.append(pygame.Surface(size=(60, 60), flags=pygame.SRCALPHA))
                self.chars[i].blit(source=font, dest=(-60*i, 0))
            elif i < 62:
                self.chars.append(pygame.Surface(size=(30, 60), flags=pygame.SRCALPHA))
                self.chars[i].blit(source=font, dest=(-60*i, 0))
            else:
                self.chars.append(pygame.Surface(size=(30, 60), flags=pygame.SRCALPHA))
                self.chars[i].blit(source=font, dest=(-60*(i-25), -60))
# f = Font("../assets/font.png")

    def make_text_surface(self, string:str, size=60, big_numbers=False) -> pygame.Surface:
        number_for = {}
        i = 0
        for char in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                     "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
                     "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7",
                     "8", "9", ".", ",", ";", "!", "?", ":", "(", ")", "*", "+", "-", "/", " "]:
            if char in "0123456789" and not big_numbers:
                number_for.update({char: (i+25)})
            else:
                number_for.update({char: i})
            i += 1

        surface_width = 0
        steps = [0]
        for char in string:
            if char in "abcdefghijklmnopqrstuvwxyz " or (char in "0123456789" and not big_numbers):
                surface_width += 30*(size/60)
                steps.append(30*(size/60))
            if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or (char in "0123456789" and big_numbers):
                surface_width += 45*(size/60)
                steps.append(45*(size/60))
            if char in ".,;!?:()*+-/":
                surface_width += 15*(size/60)
                steps.append(15*(size/60))

        text_surface = pygame.Surface(size=(surface_width*(size/60), size), flags=pygame.SRCALPHA)
        text_surface.fill((255,255,255,0))
        x_dest = 0
        i = 0
        for char in string:
            x_dest += steps[i]
            text_surface.blit(pygame.transform.scale_by(self.chars[number_for[char]], (size/60)), dest=(x_dest, 0))
            i += 1

        return text_surface