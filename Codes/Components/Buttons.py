import pygame
from Codes.Utils.SpriteFrame import SpriteFrames
from Codes.Components.AudioManager import *

class Button:
    def __init__(self, x, y, width, height, color, text, image_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 36)

        self.audio_manager = AudioManager()

        self.sfx_button_press = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/button_press.wav",
            AudioType.SFX
        )
        
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

class ButtonWithSprites(Button):
    def __init__(self, x, y, sprites, text=""):
        self.sprites : list = sprites # 0: idle, 1: hover, 2: pressed
        self.pos = (x, y)
        self.rect = self.sprites[0].get_rect(center = self.pos)
        self.current_state = self.sprites[0] # default
        self.text = text
        self._on_pressed = None

    def _on_spriteframe_finished(self):
        self.current_state = self.sprites[0]
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                collision = self.rect.collidepoint(event.pos)
                if collision:
                    self.current_state = self.sprites[1] # hover
                else:
                    self.current_state = self.sprites[0] # unhover
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                collision = self.rect.collidepoint(event.pos)
                if collision:
                    self.current_state = self.sprites[2] # pressed
                    if self._on_pressed:
                        callback = self._on_pressed
                        callback()
                    return True
                else:
                    self.current_state = self.sprites[0]
        return False

    # Draw states: Normal, be interacted, be pressed
    def draw(self, screen):
        # draw debug rect
        # pygame.draw.rect(screen, (0, 0, 0), self.rect, 3)

        # Draw image if available, otherwise draw colored rectangle
        if not self.sprites: return
        screen.blit(self.current_state, self.rect)

        # Draw text on top
        if self.text == "": return
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.current_state = self.sprites[2]
            # Play audio
            self.sfx_button_press.play()
            return self.rect.collidepoint(event.pos)
        return False