import pygame
from Codes.Scenes.SceneBase import Scene


class MainGamePlayScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        # Lưu kích thước màn hình (lấy từ game)
        self.screen_width, self.screen_height = game.screen.get_size()

        # --- Load assets ---
        self.background_picture = pygame.image.load("Assets/Images/Backgrounds/BiggerBackground.png").convert()
        self.the_machine_sprite = pygame.image.load("Assets/Images/Characters/Machine/pygameMachine.png").convert_alpha()
        self.the_robot_sprite = pygame.image.load("Assets/Images/Characters/Rabbits/TempRabbit.png").convert_alpha()

        # --- Scale background (nếu cần) ---
        bg_rect = self.background_picture.get_rect()
        if bg_rect.width != self.screen_width or bg_rect.height != self.screen_height:
            self.background_picture = pygame.transform.scale(self.background_picture, (self.screen_width, self.screen_height))

        # --- Khởi tạo vị trí nhân vật ---
        self.the_machine_pos = pygame.Vector2(250, 125)
        self.the_robot_pos = pygame.Vector2(500, 125)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Mouse button {event.button} pressed at {event.pos}")
                return True  # tiêu thụ event (nếu cần)
        return False

    def update(self, dt):
        # Đây là nơi cập nhật logic (nếu sau này có di chuyển hoặc animation)
        pass

    def draw(self, screen):
        # Vẽ nền
        screen.blit(self.background_picture, (0, 0))

        # Vẽ hai nhân vật
        screen.blit(self.the_machine_sprite, self.the_machine_pos)
        screen.blit(self.the_robot_sprite, self.the_robot_pos)
