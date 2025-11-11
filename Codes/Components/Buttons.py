class Button:
    def __init__(self, game, x, y, width, height, color, text):
        self.rect = game.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = game.font.Font(None, 36)
    
    def draw(self, game, screen):
        game.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, game, event):
        if event.type == game.MOUSEBUTTONDOWN:
            return self.rect.collidepoint(event.pos)
        return False