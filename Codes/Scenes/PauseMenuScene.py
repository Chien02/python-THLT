import pygame
from Codes.Scenes.MainGameplayScene import MainGamePlayScene
from Codes.Scenes.SceneBase import Scene
from Codes.Components.Buttons import *
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames

class PauseMenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        # surface alpha để làm overlay mờ
        self.alpha_surface = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
        self.font = pygame.font.Font(None, 72)

        # Buttons
        self.resume_button = ButtonWithImage(500, 300, "Assets/Images/UIs/Buttons/resumeButton.png")
        self.setting_button = ButtonWithImage(500, 375, "Assets/Images/UIs/Buttons/settingButton.png")
        self.home_button = ButtonWithImage(500, 450, "Assets/Images/UIs/Buttons/homeButton.png")

        # Machine's Animation
        machine_frames = FrameLoader.load_frames_from_sheet("Assets/Images/Characters/Machine/idle.png", 48, 48, 4)
        self.machine_sprite = SpriteFrames()
        self.machine_sprite.add_animation("idle", machine_frames, frame_duration=0.1)
        self.machine_sprite.play("idle")
        self.machine_pos = (200, 250)

    def handle_events(self, events):
        for event in events:
            if self.resume_button.is_clicked(event):
                print("Nút resume được nhấp!")
                # Loại bỏ pause menu scene khỏi stack
                self.game.manager.pop()
                # Resume scene nằm ngay dưới top -- TEST
                if isinstance(self.game.manager.scenes[-2], MainGamePlayScene):
                    self.game.manager.scenes[-2].paused = False
        return True  # thường menu chắn hết input, nên trả True

    def update(self, dt):
        self.machine_sprite.update(dt)
        

    def draw(self, screen):
        # overlay mờ
        alpha = 210
        self.alpha_surface.fill((0, 0, 0, alpha))  # alpha 210/255
        screen.blit(self.alpha_surface, (0, 0))
        text = self.font.render("PAUSED", True, (255, 255, 255))
        rect = text.get_rect(center=(self.game.WINDOW_WIDTH//2, self.game.WINDOW_HEIGHT//2 - 100))
        screen.blit(text, rect)
        self.resume_button.draw(screen)
        self.setting_button.draw(screen)
        self.home_button.draw(screen)
        
        # Draw animation
        SCALED_SIZE = (168, 168) # Just for testing
        current_frame = self.machine_sprite.get_current_frame()
        current_frame = pygame.transform.scale(current_frame, SCALED_SIZE)
        screen.blit(current_frame, self.machine_pos)