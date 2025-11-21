import pygame

from Codes.Scenes.SceneBase import Scene
from Codes.Components.Buttons import *
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames
from Codes.Entities.Machine.Machine import Machine
from Codes.Mechanics.Score import Score

class PauseMenuScene(Scene):
    def __init__(self, game, name='pause'):
        super().__init__(game, name)
        # surface alpha để làm overlay mờ
        self.alpha_surface = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
        self.font = pygame.font.Font(None, 72)

        # Buttons
        button_size = (144, 48)
        buttons_pos_x = (self.game.base_size[0] - button_size[1] * 8)
        buttons_pos_y = (self.game.base_size[1] // 2) - (button_size[1]*1)
        offset_y = 85
        resume_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Buttons/resume.png", button_size[0], button_size[1], 3)
        setting_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Buttons/setting.png", button_size[0], button_size[1], 3)
        home_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Buttons/home.png", button_size[0], button_size[1], 3)
        self.resume_button = ButtonWithSprites(buttons_pos_x, buttons_pos_y, resume_sprites)
        self.setting_button = ButtonWithSprites(buttons_pos_x, buttons_pos_y + offset_y, setting_sprites)
        self.home_button = ButtonWithSprites(buttons_pos_x, buttons_pos_y + offset_y * 2, home_sprites)

        # For managing buttons
        self.resume_button._on_pressed = self._on_resume_button_pressed
        self.home_button._on_pressed = self._on_home_button_pressed
        self.buttons = [self.resume_button, self.setting_button, self.home_button]

        # Machine's Animation
        machine_sprite_size = 48
        self.machine_pos = ((self.game.base_size[0] // 2) - (machine_sprite_size*3), buttons_pos_y + offset_y)
        self.machine = Machine(self.machine_pos)

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                if button.handle_events([event]): return True
            
            # For event player click on the machine
            if self.machine.handle_events([event]): return True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.resume_main_scene()

        return True  # thường menu chắn hết input, nên trả True
    
    def resume_main_scene(self):
        # Loại bỏ pause menu scene khỏi stack
        self.game.manager.pop()
        # Resume scene nằm ngay dưới top -- TEST
        from Codes.Scenes.MainGameplayScene import MainGamePlayScene
        if isinstance(self.game.manager.scenes[-2], MainGamePlayScene):
            self.game.manager.scenes[-2].paused = False

    def _on_resume_button_pressed(self):
        self.resume_main_scene()
    
    def _on_home_button_pressed(self):
        self.game.manager.back_to_scene('main_menu')

    def update(self, dt):
        self.machine.update(dt)
        self.machine.health.current_health = self.game.main_scene.machine.health.current_health

    def draw(self, screen):
        # overlay mờ
        alpha = 230
        offset_y = 175
        self.alpha_surface.fill((0, 0, 0, alpha))  # alpha 210/255
        screen.blit(self.alpha_surface, (0, 0))
        text = self.font.render("PAUSED", True, (255, 255, 255))
        rect = text.get_rect(center=(self.game.WINDOW_WIDTH//2, self.game.WINDOW_HEIGHT//2 - offset_y))
        screen.blit(text, rect)

        for button in self.buttons:
            button.draw(screen)
        
        # Draw animation
        self.machine.draw(screen)