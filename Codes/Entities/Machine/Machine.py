import pygame
from Codes.Utils.TweenAnimation import TweenAnimation
from Codes.Entities.Entity import Entity
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames
from Codes.Mechanics.Health.Health import Health

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
        self.sprite_frames.add_animation("happy", happy_sprites, frame_duration=0.05)
        self.sprite_frames.add_animation("cry", cry_sprites, frame_duration=0.1)
        self.sprite_frames.add_animation("confused", confused_sprites, frame_duration=0.1)
        self.sprite_frames.add_animation("dumb", dumb_sprites, frame_duration=0.1)
        self.sprite_frames.add_animation("over", over_sprites, frame_duration=0.1) # for game over
        self.sprite_frames.add_animation("cauvang", cauvang_sprites, frame_duration=0.1) # for "dog" strings

        # Default animation
        self.sprite_frames.set_default_animation("idle")
        self.sprite_frames.play("idle")
        self.current_state = self.sprite_frames.get_current_animation()

        # For collision detection
        # self.collide_flag = False
        self._on_animation_complete = None
        self._waiting_for_animaiton = False

        # Health
        health_offset_y = 100
        health_pos = (self.pos[0], self.pos[1] - health_offset_y)
        self.health = Health(20, health_pos) # --> Need to set its callback when machine died
    
    def update(self, dt):
        super().update(dt)
        # Machine update (visuals, tweens) done in super().update

        # Health animation update
        self.health.update(dt)

        if self._waiting_for_animaiton == False: return
        if self._is_animation_finished():
            self._waiting_for_animaiton = False

            # chuyển về default animation
            if self.health.is_alive():
                self.sprite_frames.play(self.sprite_frames.default_animation)
            
            # Gọi callback được gán cho _on_animation_complete nếu có
            if self._on_animation_complete:
                callback = self._on_animation_complete
                # self._on_animation_complete = None # Đảm bảo rằng nó ko tự gọi lại lần sau
                callback()
    
    def _is_animation_finished(self):
        """
        Kiểm tra xem animation hiện tại đã chạy xong chưa
        """
        return self.sprite_frames.is_finished()
    

    def collide_with_chatboxes(self, chatboxes: list):
        """
            Check collision against a list of chatbox objects.
            Returns the list of chatboxes collided with or None.
        """
        collided_chatboxes = []
        for cb in chatboxes:
            try:
                if self.collision_rect.colliderect(cb.collision_rect):
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
        
        # Health
        self.health.draw(screen)

