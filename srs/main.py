import pygame, json
import pawn, mask

pygame.init()

# creazione superfici
bg = pygame.image.load("backgrounds/test_9.jpg")
camera = pygame.display.set_mode((1920, 1080))
screen = pygame.surface.Surface(size=(bg.get_width(), bg.get_height()))  # serve usare una superfice ulteriore per salvare la shadow al posto dello screen, per permettere il movimento della visuale senza rompere tutto
screen.fill((255, 255, 255, 0))
room = pygame.Surface((bg.get_width(), bg.get_height()))
room.blit(bg, (0, 0))

# caricamento impostazioni
with open("srs/settings.json", "r") as file:
    room_settings = json.load(file)

zoom_factor = 1.1**float(room_settings["zoom_exponent"])
room = pygame.transform.rotozoom(room, 0, zoom_factor)
screen = pygame.transform.rotozoom(screen, 0, zoom_factor)

# creazione maschera degli ostacoli alla luce e movimento
collision_mask = mask.get_collision_mask(room, {"b":35, "r":0})

clock = pygame.time.Clock()
running = True

party = pawn.Pawn(
    position=[int(int(room_settings["starting_coords"][0])*zoom_factor), int(int(room_settings["starting_coords"][1])*zoom_factor)], 
    radius=100,
    img="backgrounds/token.png",
    size=float(room_settings["token_relative_size"]),
    zoom_factor=zoom_factor
)  # posizione iniziale storata relativa all'immagine in settings.txt

scrolling = False
camera_offset = [0, 0]
party.center_to_camera(camera, camera_offset)

while running:
    print(camera_offset)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Party movement
        if (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 
            (party.position[0] - party.texture.get_width() // 2) < pygame.mouse.get_pos()[0] < (party.position[0] + party.texture.get_width() // 2) and 
            (party.position[1] - party.texture.get_height() // 2) < pygame.mouse.get_pos()[1] < (party.position[1] + party.texture.get_height() // 2)
        ):
            party.moving = True
            party.mouse_offset = [party.position[0] - pygame.mouse.get_pos()[0], party.position[1] - pygame.mouse.get_pos()[1]]
        elif (
            event.type == pygame.MOUSEBUTTONUP and event.button == 1
        ):
            party.moving = False

        if party.moving:
            if (party.update_collision(collision_mask, (pygame.mouse.get_pos()[0] - party.hitbox_surface.get_width() // 2 - camera_offset[0], pygame.mouse.get_pos()[1] - party.hitbox_surface.get_height() // 2 - camera_offset[1]))) < 50:
                party.position = (pygame.mouse.get_pos()[0] + party.mouse_offset[0], pygame.mouse.get_pos()[1] + party.mouse_offset[1])
        
        # Screen scrolling
        if pygame.mouse.get_pressed()[0] and not party.moving:
            if not scrolling:
                scrolling = not scrolling
                last_offset = camera_offset
                last_pos = pygame.mouse.get_pos()
                last_c_pos = party.position
            else:
                camera_offset = [last_offset[0] + (pygame.mouse.get_pos()[0] - last_pos[0]), last_offset[1] + (pygame.mouse.get_pos()[1] - last_pos[1])]
                party.position = [last_c_pos[0] + (pygame.mouse.get_pos()[0] - last_pos[0]), last_c_pos[1] + (pygame.mouse.get_pos()[1] - last_pos[1])]
        else:
            scrolling = 0

        if event.type == pygame.KEYDOWN:
            # Center to party
            if event.key == pygame.K_t:
                party.center_to_camera(camera, camera_offset)

    party.update(screen, room, collision_mask, camera_offset)
    mask.get_shadow(screen, room, camera_offset, (party.position[0] - camera_offset[0], party.position[1] - camera_offset[1]), party.radius, party)
    camera.blit(screen, (0, 0))
    party.draw(camera, camera_offset)
    mask.reset_shadow((party.position[0] - camera_offset[0], party.position[1] - camera_offset[1]), party.radius)

    pygame.display.flip()
    clock.tick(60)
    print(clock.get_fps())

pygame.quit()