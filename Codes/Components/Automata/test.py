import pygame
pygame.init()
screen = pygame.display.set_mode((100, 100))

target_char = '5'
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            print(f"event key: {event.key}")
            if pygame.K_0 <= event.key <= pygame.K_9:
                pressed_num = chr(event.key)
            # Check if the character pressed matches the target character
                print(f"event's key: {pressed_num}")