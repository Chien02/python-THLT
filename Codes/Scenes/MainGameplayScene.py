import pygame
from Codes.Scenes.SceneBase import Scene
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames
from Codes.Mechanics.Chatbox.Chatbox import Chatbox


class MainGamePlayScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        # Lưu kích thước màn hình (lấy từ game)
        # Lưu kích thước màn hình logic (base size defined by Game)
        self.screen_width, self.screen_height = game.base_size

        # --- Load assets ---
        # Keep the original background so we can rescale it when the window size changes
        self._bg_orig = pygame.image.load("Assets/Images/Backgrounds/BiggerBackground.png").convert()
        self._bg_scaled = None
        self._bg_scaled_size = None

        # Temp chatbox
        self.chatbox = Chatbox(230, 400)
        self.chatbox.set_text("Hello")

        # Machine Animation
        idle_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/idle.png", 48, 48, 4)
        happy_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/happy.png", 48, 48, 4)
        cry_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/cry.png", 48, 48, 4)
        confused_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/confused.png", 48, 48, 4)

        self.machine_sprite = SpriteFrames()
        self.machine_sprite.add_animation("idle", idle_sprites, frame_duration=0.1)
        self.machine_sprite.add_animation("happy", happy_sprites, frame_duration=0.1)
        self.machine_sprite.add_animation("cry", cry_sprites, frame_duration=0.1)
        self.machine_sprite.add_animation("confused", confused_sprites, frame_duration=0.1)
        self.machine_sprite.play("idle")
        self.machine_pos = (200, 100)

    def handle_events(self, events):
        if self.chatbox.handle_events(events):
            return True
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Mouse button {event.button} pressed at {event.pos}")
                return True  # tiêu thụ event (nếu cần)
        return False

    def update(self, dt):
        # Đây là nơi cập nhật logic (nếu sau này có di chuyển hoặc animation)
        self.machine_sprite.update(dt)
        self.chatbox.update(dt)

    def draw(self, screen):
        # Vẽ nền: scale background only when screen size changes (cache result)
        cur_size = screen.get_size()
        # Note: scaling is done to the base (logical) size; the game will
        # later scale the whole render surface to the real window size.
        bg_rect = self._bg_orig.get_rect()
        if bg_rect.width != self.screen_width or bg_rect.height != self.screen_height:
            self._bg_scaled = pygame.transform.scale(self._bg_orig, (self.screen_width, self.screen_height))
            self._bg_scaled_size = (self.screen_width, self.screen_height)

        if self._bg_scaled:
            screen.blit(self._bg_scaled, (0, 0))
        else:
            screen.blit(self._bg_orig, (0, 0))

        # Draw temp chatbox
        self.chatbox.draw(screen)

        # Draw machine animation
        SCALED_SIZE = (168, 168) # Just for testing
        current_frame = self.machine_sprite.get_current_frame()
        current_frame = pygame.transform.scale(current_frame, SCALED_SIZE)
        screen.blit(current_frame, self.machine_pos)
