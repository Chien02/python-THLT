import pygame

from Codes.Scenes.SceneBase import Scene
from Codes.Scenes.StringAnalyzerScene import StringAnalyzerScene
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames
from Codes.Mechanics.Chatbox.ChatboxSpawner import ChatboxSpawner
from Codes.Mechanics.WordGenerator.BannedListGenerator import BannedListGenerator
from Codes.Mechanics.Score import Score
from Codes.Entities.Machine.Machine import Machine


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

        # Machine Animation
        machine_pos = (200, 100)
        self.machine = Machine(machine_pos)

        # Chatbox Spawner
        self.chatbox_spawner = ChatboxSpawner()

        # Analysize section
        self.is_analyzing = False
        self.anal_background = pygame.image.load("Assets/Images/Backgrounds/AnalyzingBackground.png").convert()

        # Khởi tạo Score Manager
        self.score = Score(
            correct_points=10,      # +10 điểm khi đúng
            wrong_points=-10,        # -5 điểm khi sai
            combo_multiplier=1.5    # Nhân 1.5x khi combo >= 5
        )

    def handle_events(self, events):
        for event in events:
            if self.chatbox_spawner.handle_events([event]): return True
            if self.machine.handle_events([event]): return True
        return False

    def update(self, dt):
        self.score.update(dt)
        
        self.machine.update(dt)
        self.chatbox_spawner.update(dt)
        # Collision: let the machine check against current chatboxes
        collided = self.machine.collide_with_chatboxes(self.chatbox_spawner.chatboxes)
        if collided:
            if not isinstance(self.game.manager.top(), StringAnalyzerScene):
                self.is_analyzing = True
                self.game.manager.push(StringAnalyzerScene(self.game, self, collided, self.anal_background))
                # Tạm dừng scene nằm ngay dưới top -- TEST
                if isinstance(self.game.manager.scenes[-3], MainGamePlayScene):
                    self.game.manager.scenes[-3].paused = True

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

        # Draw machine animation
        self.machine.draw(screen)

        # Draw chatboxes
        self.chatbox_spawner.draw(screen)

        # Draw score:
        self.score.draw(screen)
    
    # Callback when string analysis is done
    def get_string_analysis_done(self, results):
        self.is_analyzing = False
        for length, success in results:
            print(f"String of length {length} analysis result: {'Accepted' if success else 'Rejected'}")
