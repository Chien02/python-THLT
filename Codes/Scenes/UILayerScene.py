import pygame
from SceneBase import Scene
from Scenes.PauseMenuScene import PauseMenuScene
from Scenes.MainGameplayScene import MainGamePlayScene
from Codes.Components.Buttons import Button

class UIButtonScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.pause_button = Button(game, 300, 400, 200, 50, (0, 100, 200), "PAUSE")
    
    def handle_events(self, events):
        for event in events:
            if self.pause_button.is_clicked(event):
                print("Nút resume được nhấp!")
            # Thêm pause menu scene lên trên gameplay scene: thêm trước -> dừng sau
            if not isinstance(self.game.manager.top(), PauseMenuScene):
                self.game.manager.push(PauseMenuScene())
                # Tạm dừng scene nằm ngay dưới top -- TEST
                if isinstance(self.game.manager[-3], MainGamePlayScene):
                    self.game.manager[-3].paused = True

    def draw(self, screen):
        pass