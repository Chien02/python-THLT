import pygame
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames

class Health:
    def __init__(self, max_health, display_pos):
        self.max_health = max_health
        self.current_health = max_health
        self._on_die = None # Use for callback
        
        # Visual
        sprites_size = (96, 96)
        self.sprites_pos = display_pos
        full_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Health/full.png", sprites_size[0], sprites_size[1], 10)
        almost_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Health/4-1hp.png", sprites_size[0], sprites_size[1], 4)
        half_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Health/4-2hp.png", sprites_size[0], sprites_size[1], 4)
        low_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Health/4-3hp.png", sprites_size[0], sprites_size[1], 4)
        exhausted_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Health/exhausted.png", sprites_size[0], sprites_size[1], 5)
        temp = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Health/exhausted.png", sprites_size[0], sprites_size[1], 6)
        self.invisible_sprite = temp.pop()
        temp.clear()

        self.sprites = SpriteFrames()
        self.sprites.add_animation('full', full_sprites, frame_duration=0.1)
        self.sprites.add_animation('almost', almost_sprites, frame_duration=0.25)
        self.sprites.add_animation('half', half_sprites, frame_duration=0.25)
        self.sprites.add_animation('low', low_sprites, frame_duration=0.25)
        self.sprites.add_animation('exhausted', exhausted_sprites, frame_duration=0.25)
        self.sprites.set_default_animation('full')
        self.sprites.play('full', loop=False)

    def update(self, dt):
        if self.sprites:
            self.sprites.update(dt)
        
        # Trường hợp chạy animation cho các mức máu cụ thể
        full = self.max_health
        almost : float = (75 / 100) * self.max_health
        half : float = (50 / 100) * self.max_health
        low : float = (25 / 100) * self.max_health

        if self.current_health == full and self.sprites.current_anim != 'full':
            self.sprites.play('full', loop=False)
        elif almost <= self.current_health < full and self.sprites.current_anim != 'almost':
            self.sprites.play('almost', loop=False)
        elif half <= self.current_health < almost and self.sprites.current_anim != 'half':
            self.sprites.play('half', loop=False)
        elif low <= self.current_health < half and self.sprites.current_anim != 'low':
            self.sprites.play('low', loop=False)
        elif 0 < self.current_health < low and self.sprites.current_anim != 'exhausted':
            self.sprites.play('exhausted', loop=False)

    def draw(self, screen):
        current_sprite = self.sprites.get_current_frame() if self.is_alive() else self.invisible_sprite
        sprite_rect = current_sprite.get_rect(center=self.sprites_pos)
        screen.blit(current_sprite, sprite_rect)

    def take_damage(self, amount):
        self.current_health = max(0, self.current_health - amount)
        print(f"Trừ máu, hiện tại còn lại: {self.current_health}")
        print(f"Anim hiện tại {self.sprites.current_anim}")

        if self.current_health != 0: return
        if self._on_die:
            callback = self._on_die
            callback()

    def heal(self, amount):
        self.current_health = min(self.max_health, self.current_health + amount)

    def get_current_health(self):
        return self.current_health

    def is_alive(self):
        return self.current_health > 0