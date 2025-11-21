import pygame
from Codes.Scenes.SceneBase import Scene

class SettingScene(Scene):
    def __init__(self, game, name='setting'):
        super().__init__(game, name)


    
    def update(self, dt):
        pass

    def handle_events(self, events):
        for event in events:
            pass
        return True

    def draw(self, screen):
        """
            Title, button, slider để tăng giảm âm lượng cho sound và music.
        """