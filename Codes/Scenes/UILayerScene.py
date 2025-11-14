import pygame
from Codes.Scenes.SceneBase import Scene
from Codes.Scenes.PauseMenuScene import PauseMenuScene
from Codes.Scenes.MainGameplayScene import MainGamePlayScene
from Codes.Components.Buttons import *

class UILayerScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.pause_button = ButtonWithImage(680, 20, "Assets/Images/UIs/Buttons/pauseButton.png")
    
    def handle_events(self, events):
        for event in events:
            if self.pause_button.is_clicked(event):
                # Thêm pause menu scene lên trên gameplay scene: thêm trước -> dừng sau
                if not isinstance(self.game.manager.top(), PauseMenuScene):
                    self.game.manager.push(PauseMenuScene(self.game))
                    # Tạm dừng scene nằm ngay dưới top -- TEST
                    if isinstance(self.game.manager.scenes[-3], MainGamePlayScene):
                        self.game.manager.scenes[-3].paused = True
                    return True # Comsume event
        return False

    def draw(self, screen):
        self.pause_button.draw(screen)