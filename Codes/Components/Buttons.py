import pygame

class Button:
    def __init__(self, x, y, width, height, color, text, image_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 36)
        
        # Load image if provided
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                # Set button size to image size
                self.rect.width = self.image.get_width()
                self.rect.height = self.image.get_height()
            except Exception as e:
                print(f"Warning: Could not load button image '{image_path}': {e}")
                self.image = None
    
    def draw(self, screen):
        # Draw image if available, otherwise draw colored rectangle
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw text on top
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.rect.collidepoint(event.pos)
        return False

class ButtonWithImage(Button):
    def __init__(self, x, y, image_path, text=""):
        super().__init__(x, y, 0, 0, (0,0,0), text, image_path)