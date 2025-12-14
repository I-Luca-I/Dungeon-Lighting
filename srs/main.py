import pygame
import camera, mask

# TODO - importanti:
# - cancellare raggi isolati (errori)
# - pedina
# - zoom
# - salvataggio luce

# TODO - sarebbe figo:
# - doors
# - collisioni
# - raytracing
# - cool ass fog

pygame.init()
bg = pygame.image.load("backgrounds/test_8.jpg")
screen = pygame.display.set_mode((bg.get_width(), bg.get_height()))
room = pygame.Surface((bg.get_width(), bg.get_height()))
room.blit(bg, (0, 0))
collision_mask = mask.get_collision_mask(room, {"b":35, "r":0})
clock = pygame.time.Clock()
running = True

c = camera.Camera(position=(640, 360), radius=100)
pygame.time.set_timer(pygame.USEREVENT, 200)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(bg, (0, 0))
    c.position = pygame.mouse.get_pos()
    c.update(screen, room, collision_mask)
    screen = mask.get_shadow(screen, room)

    pygame.display.flip()
    clock.tick(60)
    print(clock.get_fps())

pygame.quit()