import pygame
from Codes.Utils.TweenAnimation import TweenAnimation
from Codes.Entities.Entity import Entity
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames

class Machine(Entity):
    def __init__(self, pos):
        super().__init__(pos)

        # Loads animations
        sprite_size_x = 144
        sprite_size_y = 144
        idle_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/idle.png", sprite_size_x, sprite_size_y, 4)
        happy_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/happy.png", sprite_size_x, sprite_size_y, 4)
        cry_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/cry.png", sprite_size_x, sprite_size_y, 4)
        confused_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/confused.png", sprite_size_x, sprite_size_y, 4)
        dumb_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/dumb.png", sprite_size_x, sprite_size_y, 4)
        over_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/over.png", sprite_size_x, sprite_size_y, 4)
        cauvang_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/cauvang.png", sprite_size_x, sprite_size_y, 4)

        # Add animations to sprite_frame
        self.sprite_frames.add_animation("idle", idle_sprites, frame_duration=0.1)
        self.sprite_frames.add_animation("happy", happy_sprites, frame_duration=0.1)
        self.sprite_frames.add_animation("cry", cry_sprites, frame_duration=0.1)
        self.sprite_frames.add_animation("confused", confused_sprites, frame_duration=0.1)
        self.sprite_frames.add_animation("dumb", dumb_sprites, frame_duration=0.1)
        self.sprite_frames.add_animation("over", over_sprites, frame_duration=0.1) # for game over
        self.sprite_frames.add_animation("cauvang", cauvang_sprites, frame_duration=0.1) # for "dog" strings

        # Default animation
        self.sprite_frames.set_default_animation("idle")
        self.sprite_frames.play("idle")

        # For collision detection
        # self.collide_flag = False
    
    def update(self, dt):
        super().update(dt)
        # Machine update (visuals, tweens) done in super().update

    def collide_with_chatboxes(self, chatboxes: list):
        """Check collision against a list of chatbox objects.

        Returns the list of chatboxes collided with or None.
        """
        collided_chatboxes = []
        for cb in chatboxes:
            try:
                if self.collision_rect.colliderect(cb.collision_rect):
                    # Play 'happy' animation on collision
                    self.sprite_frames.play("happy", loop=False)
                    cb.die()
                    collided_chatboxes.append(cb)
            except Exception:
                # If chatbox has no collision_rect or it's invalid, skip
                continue
        return collided_chatboxes if collided_chatboxes else None
    
    def handle_events(self, events):
        for event in events:
            super().handle_events([event])
            return False
    
    def draw(self, screen):
        super().draw(screen)

