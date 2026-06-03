import pygame

class Font:
    def __init__(self, path:str) -> None:
        self.chars:list[pygame.Surface] = []
        font = pygame.image.load(path)
        for i in range(62):
            self.chars.append(pygame.Surface(size=(60, 60), flags=pygame.SRCALPHA))
            self.chars[i].blit(source=font, dest=(60*i, 0))

# f = Font("../assets/font.png")
