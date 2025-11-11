import pygame
from Codes.Scenes.SceneBase import Scene

class PauseMenuScene(Scene):
    def __init__(self):
        # surface alpha để làm overlay mờ
        self.alpha_surface = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
        self.font = pygame.font.Font(None, 72)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    # tiêu thụ event và yêu cầu manager đóng menu
                    self.game.manager.pop()

                    # để gameplay scene hết paused
                    if self.game.manager.scenes[-1]:
                        self.game.manager.scenes[-1].paused = False
                    return True
        # nếu không xử lý gì -> trả False để event có thể truyền xuống (tuỳ ý)
        return True  # thường menu chắn hết input, nên trả True

    def draw(self, screen):
        # overlay mờ
        self.alpha_surface.fill((0, 0, 0, 150))  # alpha 150/255
        screen.blit(self.alpha_surface, (0, 0))
        text = self.font.render("PAUSED", True, (255, 255, 255))
        rect = text.get_rect(center=(self.game.WINDOW_WIDTH//2, self.game.WINDOW_HEIGHT//2))
        screen.blit(text, rect)