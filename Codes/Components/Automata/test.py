import pygame

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame get_rect(center) Example")

# Create a sample surface (e.g., a text surface)
font = pygame.font.Font(None, 50)
text_surface = font.render("Hello, Pygame!", True, (255, 255, 255)) # White text

# Get the rect of the text surface, centered at specific coordinates
# For example, to center it in the middle of the screen:
center_x = screen_width // 2
center_y = screen_height // 2
text_rect = text_surface.get_rect(center=(center_x, center_y))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with black
    screen.fill((0, 0, 0))

    # Blit the text surface onto the screen at the calculated rect position
    screen.blit(text_surface, text_rect)

    # Update the display
    pygame.display.flip()

pygame.quit()
