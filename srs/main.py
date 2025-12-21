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

# creazione superfici
bg = pygame.image.load("backgrounds/test_9.jpg")
token = pygame.image.load("backgrounds/token.png")
screen = pygame.display.set_mode((1500, 1500))
shadow_surf = pygame.surface.Surface(size=(bg.get_width(), bg.get_height()))  # serve usare una superfice ulteriore per salvare la shadow al posto dello screen, per permettere il movimento della visuale senza rompere tutto
shadow_surf.fill((255,255,255,0))
room = pygame.Surface((bg.get_width(), bg.get_height()))
room.blit(bg, (0, 0))

# setup zoom e grandezza token
with open("settings.txt") as f:
    room_settings = f.readlines()
    for line in room_settings:
        line.replace("\n", "")
zoom_factor = 1.1**float(room_settings[0])
room = pygame.transform.rotozoom(room, 0, zoom_factor)
shadow_surf = pygame.transform.rotozoom(shadow_surf, 0, zoom_factor)
token = pygame.transform.rotozoom(token, 0, float(room_settings[1]) / token.get_width())

camera_wall_coll_surf = pygame.surface.Surface(size=((token.get_width()//3), (token.get_height()//3)))  # superficie utilizzata per controllare le colisioni fra muri e token/camera

# creazione maschera degli ostacoli alla luce e movimento
collision_mask = mask.get_collision_mask(room, {"b":35, "r":0})

clock = pygame.time.Clock()
running = True

moving = False

c = camera.Camera(position=[int(int(room_settings[2])*zoom_factor), int(int(room_settings[3])*zoom_factor)], radius=100)  # posizione iniziale storata relativa all'immagine in settings.txt

scrolling = False
screen_offset = [0, 0]

pygame.time.set_timer(pygame.USEREVENT, 200)


def center_token():
    delta_x = int(c.position[0] / zoom_factor - screen.get_width() / 2)
    delta_y = int(c.position[1] / zoom_factor - screen.get_height() / 2)
    screen_offset[0] -= delta_x
    screen_offset[1] -= delta_y
    c.position = [c.position[0] - delta_x, c.position[1] - delta_y]


def check_camera_wall_collisions(camera_box_surf, wall_mask, offset):
    pygame.draw.circle(camera_box_surf, (255, 0, 0), (camera_box_surf.get_width() // 2, camera_box_surf.get_height() // 2), camera_box_surf.get_height() // 2)
    camera_box_mask = pygame.mask.from_threshold(camera_box_surf, (255, 0, 0), (35, 35, 35, 0))
    return wall_mask.overlap_area(camera_box_mask, offset)


center_token()

while running:
    print(screen_offset)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (c.position[0] - token.get_width() // 2) < pygame.mouse.get_pos()[0] < (c.position[0] + token.get_width() // 2) and (c.position[1] - token.get_height() // 2) < pygame.mouse.get_pos()[1] < (c.position[1] + token.get_height() // 2):
            moving = not moving
        elif pygame.mouse.get_pressed()[0]:
            if not scrolling:
                scrolling = not scrolling
                last_offset = screen_offset
                last_pos = pygame.mouse.get_pos()
                last_c_pos = c.position
            else:
                screen_offset = [last_offset[0] + (pygame.mouse.get_pos()[0] - last_pos[0]), last_offset[1] + (pygame.mouse.get_pos()[1] - last_pos[1])]
                c.position = [last_c_pos[0] + (pygame.mouse.get_pos()[0] - last_pos[0]), last_c_pos[1] + (pygame.mouse.get_pos()[1] - last_pos[1])]
        else:
            scrolling = 0
        if moving:
            if check_camera_wall_collisions(camera_wall_coll_surf, collision_mask, (pygame.mouse.get_pos()[0] - camera_wall_coll_surf.get_width() // 2 - screen_offset[0], pygame.mouse.get_pos()[1] - camera_wall_coll_surf.get_height() // 2 - screen_offset[1])) < 5:
                c.position = list(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                center_token()

    c.update(shadow_surf, room, collision_mask, screen_offset)
    mask.get_shadow(shadow_surf, room, screen_offset)
    screen.blit(shadow_surf, (0, 0))
    screen.blit(token, (c.position[0] - token.get_width() // 2, c.position[1] - token.get_height() // 2))
    # screen.blit(camera_wall_coll_surf, (c.position[0] - camera_wall_coll_surf.get_width() // 2, c.position[1] - camera_wall_coll_surf.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)
    print(clock.get_fps())

pygame.quit()