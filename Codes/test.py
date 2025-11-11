import pygame

pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Drag and Drop Image")

clock = pygame.time.Clock()

image = pygame.image.load("Assets/Images/Elements/Chatbox/chatbox1.png").convert_alpha() # Replace "your_image.png"
image_rect = image.get_rect(center=(screen_width // 2, screen_height // 2))

running = True
dragging = False
offset_x, offset_y = 0, 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if image_rect.collidepoint(event.pos):
                dragging = True
                mouse_x, mouse_y = event.pos
                offset_x = image_rect.x - mouse_x
                offset_y = image_rect.y - mouse_y
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x, mouse_y = event.pos
                image_rect.x = mouse_x + offset_x
                image_rect.y = mouse_y + offset_y
        # Drawing
        screen.fill("black")  # Fill background with black
        screen.blit(image, image_rect)
        pygame.display.flip()
    clock.tick(60)

pygame.quit()