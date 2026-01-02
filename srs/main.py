import pygame, json
import pawn, mask

pygame.init()

# creazione superfici
bg_name = "test_13"
bg = pygame.image.load(f"backgrounds/{bg_name}.png")
camera = pygame.display.set_mode((1000, 500))
screen = pygame.surface.Surface(size=(bg.get_width(), bg.get_height()))  # serve usare una superfice ulteriore per salvare la shadow al posto dello screen, per permettere il movimento della visuale senza rompere tutto
screen.fill((255, 255, 255, 0))
room = pygame.Surface((bg.get_width(), bg.get_height()))
room.blit(bg, (0, 0))

# caricamento impostazioni
with open("settings.json", "r") as file:
    room_settings = json.load(file)

zoom_factor = 1.1**float(room_settings["zoom_exponent"])
room = pygame.transform.rotozoom(room, 0, zoom_factor)
screen = pygame.transform.rotozoom(screen, 0, zoom_factor)

# Cursore fighissimo pazzo
cursore_0_img = pygame.image.load("backgrounds/cursor0.png")
cursore_0_img = pygame.transform.rotozoom(cursore_0_img, 315, (70/cursore_0_img.get_width())*zoom_factor)
cursore0 = pygame.cursors.Cursor((7, 28), cursore_0_img)
cursore_1_img = pygame.image.load("backgrounds/cursor1.png")
cursore_1_img = pygame.transform.rotozoom(cursore_1_img, 315, (70/cursore_1_img.get_width())*zoom_factor)
cursore1 = pygame.cursors.Cursor((7, 28), cursore_1_img)
cursori = [cursore0, cursore1]
pygame.mouse.set_cursor(cursori[0])

# creazione maschera degli ostacoli alla luce e movimento e maschera porte
collision_mask = mask.get_collision_mask(room, {"b":35, "r":0})
door_surf = pygame.image.load(f"backgrounds/{bg_name}_doors.png")
door_surf = pygame.transform.rotozoom(door_surf, 0, zoom_factor)
door_mask = mask.get_door_mask(door_surf)
door_test_surf = door_mask.to_surface(unsetcolor=None)
doors = mask.get_doors(door_surf, door_mask, door_test_surf)


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

save_num = room_settings["save_number"]

def save():
    global save_num
    save_num += 1
    settings = {
        "zoom_exponent": room_settings["zoom_exponent"],
        "token_relative_size": room_settings["token_relative_size"],
        "starting_coords": room_settings["starting_coords"],
        "save_number": save_num
    }
    with open("settings.json", "w") as f:
        json.dump(settings, f)
    save_surf = mask.get_save_surface(room.convert_alpha())
    pygame.image.save(save_surf, f"saves/save{save_num}.png")


while running:
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
            pygame.mouse.set_cursor(cursori[0])

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

        if pygame.mouse.get_pressed()[0]:
            pygame.mouse.set_cursor(cursori[1])

        if pygame.mouse.get_pressed()[0] and mask.check_door_click(door_mask, (pygame.mouse.get_pos()[0] - camera_offset[0], pygame.mouse.get_pos()[1] - camera_offset[1])):
            smaller_distance = 0
            for coord in doors:
                if smaller_distance == 0 or abs(pygame.mouse.get_pos()[0] - camera_offset[0] - coord[0]) + abs(pygame.mouse.get_pos()[1] - camera_offset[1] - coord[1]) < smaller_distance:
                    smaller_distance = abs(pygame.mouse.get_pos()[0] - camera_offset[0] - coord[0]) + abs(pygame.mouse.get_pos()[1] - camera_offset[1] - coord[1])
                    door = [doors[coord], coord]
            collision_mask.erase(door[0], door[1])

        if event.type == pygame.KEYDOWN:
            # Center to party
            if event.key == pygame.K_t:
                party.center_to_camera(camera, camera_offset)
            # Discovered map saving
            if event.key == pygame.K_s:
                save()

    party.update(screen, room, collision_mask, camera_offset)
    mask.get_shadow(screen, room, camera_offset, (party.position[0] - camera_offset[0], party.position[1] - camera_offset[1]), party.radius, party)
    camera.blit(screen, (0, 0))
    party.draw(camera, camera_offset)
    mask.reset_shadow((party.position[0] - camera_offset[0], party.position[1] - camera_offset[1]), party.radius)
    # camera.blit(door_test_surf, camera_offset)

    pygame.display.flip()
    clock.tick(60)
    print(clock.get_fps())

save()
pygame.quit()
