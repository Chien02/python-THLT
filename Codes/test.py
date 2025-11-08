import pygame, sys

from pygame.locals import * # Import game's modules

class Game:
# ---- Variables ------
# UI's properties
    def __init__(self):
        SCALED_RATIO = 4
        max_width = 256 * SCALED_RATIO
        max_height = 192 * SCALED_RATIO
        center_value = ((max_height ** 2 + max_width ** 2) ** 0.5) / 2
        self.center_pos = (center_value, center_value)
        self.window_size = (max_width, max_height)
        self.game_title = "Langua Machine Game"

        # UI's sprites
        self.background_picture = pygame.image.load("Assets/Images/Backgrounds/BiggerBackground.png")

        # Characters
        # --- The machine
        self.the_machine_sprite = pygame.image.load("Assets/Images/Characters/Machine/pygameMachine.png")
        self.the_machine_init_pos = [250, 125]

        # --- The player's character
        self.player_init_pos = [250, 400]
        self.player_sprite = pygame.image.load("Assets/Images/Characters/Rabbits/TempRabbit.png")
        self.player_speed = 4
        self.player_pos = self.player_init_pos
        self.player_movement_y = [False, False]
        self.player_movement_x = [False, False]

        # Systems or Mechanic or Game Loop
        self.clock = pygame.time.Clock() # This is important
        self.delta_time = 0.85

        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size, 0, 32)
        pygame.display.set_caption(f"{self.game_title}")

    def run(self):
        # ----- Game Loop ------
        while True:
            # Player's movement
            self.player_pos[0] += (self.player_movement_x[1] - self.player_movement_x[0]) * self.player_speed
            self.player_pos[1] += (self.player_movement_y[1] - self.player_movement_y[0]) * self.player_speed

            # Insert the images to the window
            self.screen.blit(self.background_picture, (0, 0))
            self.screen.blit(self.the_machine_sprite, self.the_machine_init_pos)
            self.screen.blit(self.player_sprite, self.player_init_pos)

            # Get the event for every frame that render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # INPUT - to move the character:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.player_movement_y[0] = True
                    if event.key == pygame.K_DOWN:
                        self.player_movement_y[1] = True
                    if event.key == pygame.K_LEFT:
                        self.player_movement_x[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.player_movement_x[1] = True
                
                # When stop input for stop moving
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.player_movement_y[0] = False
                    if event.key == pygame.K_DOWN:
                        self.player_movement_y[1] = False
                    if event.key == pygame.K_LEFT:
                        self.player_movement_x[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.player_movement_x[1] = False

            pygame.display.update()
            self.clock.tick(60) # Maintain 30 fps
    
Game().run()