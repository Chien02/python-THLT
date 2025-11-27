import pygame
from tweener import *
from Codes.Utils.SpriteFrame import SpriteFrames

# ENTITY SPRITE SIZE CONSTANTS
SPRITE_SIZE = (144, 144)

# Tween constants
SQUASH_SCALE = 0.5
STRETCH_SCALE = 1.5
RESET_SCALE = 1.0

class Entity:
    def __init__(self, pos: tuple[int, int], collision_rect_size: tuple[int, int]=SPRITE_SIZE):
        self.pos = pos
        self.collision_rect = None  # Use provided size
        self.sprite_frames = SpriteFrames()
        self.tween = None  # Placeholder for tween animation
        self.scale = 1.0  # Initial scale for drawing

        self.pending_reset = False  # Flag to indicate if we need to reset scale after stretch

    # Tween animations
    def squash(self):  # thu nhỏ (khi nén)
        self.tween = Tween(
            begin=self.scale,
            end=SQUASH_SCALE,  # thu nhỏ còn 50%
            duration=150, # milliseconds
            easing=Easing.BACK,
            easing_mode=EasingMode.IN
        )
        self.tween.start()

    def stretch(self):  # phồng ra (khi nhấn)
        self.tween = Tween(
            begin=self.scale,
            end=STRETCH_SCALE,  # phình ra hơn bình thường
            duration=250, # milliseconds
            easing=Easing.ELASTIC,
            easing_mode=EasingMode.OUT
        )
        self.tween.start()
        self.pending_reset = True
    
    def reset_scale(self):
        self.tween = Tween(
            begin=self.scale,
            end=RESET_SCALE,  # trở về kích thước ban đầu
            duration=500, # milliseconds
            easing=Easing.BACK,
            easing_mode=EasingMode.OUT
        )
        self.tween.start()


    def update(self, dt: float):
        self.sprite_frames.update(dt)

        # cập nhật tween mỗi frame
        if self.tween and self.tween.animating:
            self.tween.update()
            self.scale = self.tween.value

        if self.tween and not self.tween.animating:
            self.tween = None  # Xóa tween khi hoàn thành

            if self.pending_reset:
                self.pending_reset = False
                self.reset_scale()
    

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.collision_rect.collidepoint(event.pos):
                    self.stretch()
                    return True
        return False
    
    def draw(self, screen):
        current_frame = self.sprite_frames.get_current_frame()
        self.collision_rect = current_frame.get_rect(center=self.pos)
        if current_frame is None:
            return

        # Scale frame hiện tại
        w, h = current_frame.get_size()
        # Prevent zero-sized scale which causes transform errors
        scaled_w, scaled_h = max(1, int(w * self.scale)), max(1, int(h * self.scale))
        try:
            scaled_frame = pygame.transform.scale(current_frame, (scaled_w, scaled_h))
        except Exception:
            # As a last resort, just use the original frame
            scaled_frame = current_frame
        # Position the sprite so it scales around the collision rect center
        # This keeps the collision rect fixed while the sprite grows/shrinks
        rect = scaled_frame.get_rect(center=self.collision_rect.center)
        screen.blit(scaled_frame, rect)

        # # For debugging: draw collision rect
        # pygame.draw.rect(screen, (255, 0, 0), self.collision_rect, 1)
        
