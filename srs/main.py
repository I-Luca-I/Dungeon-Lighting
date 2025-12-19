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
bg = pygame.image.load("backgrounds/test_10.jpg")
token = pygame.image.load("backgrounds/token.png")
screen = pygame.display.set_mode((bg.get_width(), bg.get_height()))
shadow_surf = pygame.surface.Surface(size=(1500, 1500))  # serve usare una superfice ulteriore per salvare la shadow al posto dello screen, per permettere il movimento della visuale senza rompere tutto
shadow_surf.fill((255,255,255,0))
room = pygame.Surface((bg.get_width(), bg.get_height()))
room.blit(bg, (0, 0))
# setup zoom e grandezza token
with open("settings.txt") as f:
    room_settings = f.readlines()
    for line in room_settings:
        line.replace("\n", "")
zoom_factor = (1.1)**float(room_settings[0])
room = pygame.transform.rotozoom(room, 0, zoom_factor)
shadow_surf = pygame.transform.rotozoom(shadow_surf, 0, zoom_factor)
token = pygame.transform.rotozoom(token, 0, float(room_settings[1]) / token.get_width())
collision_mask = mask.get_collision_mask(room, {"b":35, "r":0})
clock = pygame.time.Clock()
running = True
moving = False
screen_offset = [0, 0]

c = camera.Camera(position=[int(int(room_settings[2])*zoom_factor), int(int(room_settings[3])*zoom_factor)], radius=100)  # posizione iniziale storata relativa all'immagine in settings.txt
pygame.time.set_timer(pygame.USEREVENT, 200)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (c.position[0] - token.get_width() // 2) < pygame.mouse.get_pos()[0] < (c.position[0] + token.get_width() // 2) and (c.position[1] - token.get_height() // 2) < pygame.mouse.get_pos()[1] < (c.position[1] + token.get_height() // 2):
            moving = not moving
        if moving:
            c.position = list(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                screen_offset[1] -= bg.get_height()//10
                c.position[1] -= bg.get_height()//10
            if event.key == pygame.K_UP:
                screen_offset[1] += bg.get_height()//10
                c.position[1] += bg.get_height()//10
            if event.key == pygame.K_RIGHT:
                screen_offset[0] -= bg.get_height()//10
                c.position[0] -= bg.get_height()//10
            if event.key == pygame.K_LEFT:
                screen_offset[0] += bg.get_height()//10
                c.position[0] += bg.get_height()//10

    # screen.blit(room, screen_offset)
    c.update(shadow_surf, room, collision_mask, screen_offset)
    mask.get_shadow(shadow_surf, room, screen_offset)
    screen.blit(shadow_surf, (0,0))
    # token
    screen.blit(token, (c.position[0] - token.get_width() // 2, c.position[1] - token.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)
    print(clock.get_fps())

pygame.quit()