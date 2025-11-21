import pygame
from Codes.Scenes.SceneBase import Scene
from Codes.Scenes.MainGameplayScene import MainGamePlayScene
from Codes.Scenes.UILayerScene import UILayerScene
from Codes.Components.Buttons import *
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames

class MainMenuScene(Scene):
    def __init__(self, game, name='main_menu'):
        super().__init__(game, name)

        # Các thuộc tính và hình ảnh
        offset_x = 130
        offset_y = 100
        spacing = 60
        self.align_x = self.game.base_size[0] - offset_x

        button_size = (144, 48)
        button_pos_x = self.align_x - (button_size[0] // 2)
        button_pos_y = (self.game.base_size[1] // 2) + offset_y
        self.play_btn_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Buttons/resume.png", button_size[0], button_size[1], 3)
        self.setting_btn_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Buttons/setting.png", button_size[0], button_size[1], 3)
        self.play_btn = ButtonWithSprites(button_pos_x, button_pos_y, self.play_btn_sprites)
        self.setting_btn = ButtonWithSprites(button_pos_x, button_pos_y + spacing * 1, self.setting_btn_sprites)

        self.play_btn._on_pressed = self._on_play_btn_pressed
        self.setting_btn._on_pressed = self._on_setting_btn_pressed

        self.buttons = [self.play_btn, self.setting_btn]
    
    def _on_play_btn_pressed(self):
        """
            Thêm main_game scene và ui scene lên top của manager
        """
        if not self.game.main_scene: # Lần đầu vào game, main_game và ui chưa được thêm vào stack
            new_scene = MainGamePlayScene(self.game)
            self.game.main_scene = new_scene
            new_ui_scene = UILayerScene(self.game)

            self.game.manager.push(new_scene)
            self.game.manager.push(new_ui_scene)
        else: # main_game đã có nhưng bị xóa khỏi tách
            self.game._on_reload_main_scene()
    
    def _on_setting_btn_pressed(self):
        """
            Thêm setting scene vào top
        """
        # Sẽ thêm vào sau - 20/11/2025: hiện chưa có
        pass

    def update(self, dt):
        pass

    def handle_events(self, events): # return true or false
        for event in events:
            for button in self.buttons:
                if button.handle_events([event]): return True
        return False
    
    def draw(self, screen):
        """
            Hiển thị background chính, title, 2 nút [play, setting]
            Khi nút play được bấm, gọi callback thêm 2 scene (MainGamePlayScene, UILayerScene)
        """
        # Tittle
        WHITE = (255, 255, 255)
        font = pygame.font.Font(None, 67)
        offset_y = 75
        title_pos_x = self.align_x
        title_pos_y = self.game.base_size[1] * 1 // 4

        game_title_1 = "THE LANGUAGE"
        game_title_2 = "MACHINE"
        title1_surface = font.render(game_title_1, True, WHITE)
        title2_surface = font.render(game_title_2, True, WHITE)
        title1_rect = title1_surface.get_rect(topright = (title_pos_x, title_pos_y))
        title2_rect = title2_surface.get_rect(topright = (title_pos_x, title_pos_y + offset_y))

        screen.blit(title1_surface, title1_rect)
        screen.blit(title2_surface, title2_rect)

        # Buttons
        for button in self.buttons:
            button.draw(screen)