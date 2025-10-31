import pygame, sys

from pygame.locals import * # Import game's modules

# ---- Variables ------
# UI's properties
game_title = "FA Simulation"
SCALED_RATIO = 4
max_width = 256 * SCALED_RATIO
max_height = 192 * SCALED_RATIO
window_size = (max_width, max_height)

# UI's sprites
background_picture = pygame.image.load("Assets/Images/Backgrounds/GrassBackgrounds.png")

# Characters
player_sprite_init_pos = (100, 100)
player_sprite = pygame.image.load("Assets/Images/Characters/Rabbits/TempRabbit.png")

# Systems or Mechanic or Game Loop
clock = pygame.time.Clock()

pygame.init()
screen = pygame.display.set_mode(window_size, 0, 32)
pygame.display.set_caption(f"{game_title}")


# ----- Game Loop ------
while True:
    for event in pygame.event.get():
        # Mechanics go down here
        screen.blit(background_picture, (0, 0))
        screen.blit(player_sprite, player_sprite_init_pos)

        if event.type == QUIT:
            pygame.quit() # Stop pygame
            sys.exit() # Stop script
    
    pygame.display.update()
    clock.tick(30) # Maintain 30 fps
    
