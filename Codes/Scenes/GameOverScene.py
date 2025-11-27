import pygame

from Codes.Scenes.SceneBase import Scene
from Codes.Components.Buttons import *
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames
from Codes.Entities.Machine.Machine import Machine
from Codes.Mechanics.Score import Score

class GameOverScene(Scene):
    def __init__(self, game, name='over'):
        super().__init__(game, name)
        # surface alpha để làm overlay mờ
        self.alpha_surface = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
        self.font = pygame.font.Font(None, 72)

        # Buttons
        center = ((self.game.base_size[0] // 2), (self.game.base_size[1] // 2))
        button_size = (144, 48)
        buttons_pos_x = center[0] - 120
        buttons_pos_y = center[1] + (button_size[1]*3)
        offset_y = 85
        offset_x = button_size[0] + (button_size[0] // 3)
        replay_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Buttons/replay.png", button_size[0], button_size[1], 3)
        home_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Buttons/home.png", button_size[0], button_size[1], 3)
        self.replay_button = ButtonWithSprites(buttons_pos_x, buttons_pos_y + offset_y, replay_sprites)
        self.home_button = ButtonWithSprites(buttons_pos_x + offset_x, buttons_pos_y + offset_y, home_sprites)

        # For managing buttons
        self.replay_button._on_pressed = self._on_replay_button_pressed
        self.home_button._on_pressed = self._on_home_button_pressed
        self.buttons = [self.replay_button, self.home_button]

        # Machine's Animation
        machine_sprite_size = 144
        self.machine_pos = (center[0] - (machine_sprite_size*1), center[1])
        self.machine = Machine(self.machine_pos)
        self.machine.sprite_frames.set_default_animation('over')
        self.machine.sprite_frames.play('over')

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                if button.handle_events([event]): return True
        return True  # thường menu chắn hết input, nên trả True

    def _on_replay_button_pressed(self):
        # Play audio
        self.game.audio.play_sfx('button_press')
        self.paused = True
        self.game.manager.pop()
        self.game._on_reload_main_scene()
    
    def _on_home_button_pressed(self):
        # Play audio
        self.game.audio.play_sfx('button_press')
        self.paused = True
        self.game.manager.back_to_scene('man_menu')

    def on_enter(self):
        # Play gameover sound effect when enter scene
        if self.game:
            self.game.audio.play_sfx('gameover')

    def update(self, dt):
        # Play audio
        self.game.audio.play_bgm('gameover')

        self.machine.update(dt)
        self.machine.health.current_health = self.game.main_scene.machine.health.current_health

    # Color
    RED = (174, 35, 52)
    YELLOW = (255, 215, 0)
    def draw(self, screen):
        # overlay mờ
        # Background overlay
        screen_size = self.game.base_size
        overlay = pygame.Surface((screen_size[0], screen_size[1]))
        overlay.set_alpha(235)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Title
        offset_y = 200
        text = self.font.render("GAME OVER", True, self.YELLOW)
        rect = text.get_rect(center=(self.game.WINDOW_WIDTH//2, self.game.WINDOW_HEIGHT//2 - offset_y))
        screen.blit(text, rect)

        for button in self.buttons:
            button.draw(screen)
        
        # Draw animation
        self.machine.draw(screen)

        # Draw summary
        summary_rect = pygame.rect.Rect(560, 300, 330, 350)
        # summary_panel_pos = (680, 390)
        self.game.score.draw_summary(screen, self.game.base_size)