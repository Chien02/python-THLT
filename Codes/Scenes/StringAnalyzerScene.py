import pygame
import json
from Codes.Scenes.SceneBase import Scene
from Codes.Components.Automata.FA import FA
from Codes.Mechanics.WordGenerator.BannedListGenerator import BannedListGenerator
from Codes.Mechanics.Timer import Timer
from Codes.Mechanics.Score import Score
from Codes.Utils.FrameLoader import FrameLoader

class StringAnalyzerScene(Scene):
    def __init__(self, game, main_scene, collided_chatboxes: list, background):
        super().__init__(game)
        from Codes.Scenes.MainGameplayScene import MainGamePlayScene
        self.main_scene : MainGamePlayScene = main_scene
        self.collided_chatboxes = collided_chatboxes
        self._bg_orig = background

        self.screen_width, self.screen_height = game.base_size
        self._bg_scaled = None
        self._bg_scaled_size = None

        # Load assets
        frame_size = (90, 90)
        self.state_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Diagram/circles.png", frame_size[0], frame_size[1], 4)

        # Add texts from collided chatboxes
        self.texts = []
        if self.collided_chatboxes:
            for cb in self.collided_chatboxes:
                self.texts.append(cb.text)
        
        self.current_text_index = 0
        if self.texts:
            self.current_text = self.texts[self.current_text_index]
        self.pattern_pos = (self.screen_width // 2, self.screen_height - 135)

        # keywords
        self.keywords = self.load_keywords("Data/keywords.json")["keywords"]

        # Init Timer
        self.timer = Timer(duration=10.0, auto_start=False)
        self.timer.on_timeout = self.on_timer_timeout  # Set callback

        # Init_FA based on text
        self.fa : FA = FA(self, self.current_text, self.game.base_size)

        # Dừng lại khi xử lý hết chatbox được truyền vào:
        if self.current_text_index != len(self.texts):
            self.analyzing = True
        else:
            self.analyzing = False
        
        #  Start timer sau khi FA vẽ xong
        self.timer.start()

    def handle_events(self, events):
        for event in events:
            # Handle events specific to String Analyzer Scene
            return self.fa.handle_events([event])
        return True

    def update(self, dt):
        # update score if main scene is pause
        if self.main_scene.paused:
            self.main_scene.score.update(dt)

        # Update timer
        self.timer.update(dt)

        self.fa.update(dt)

        # Nếu ngưng analyzing thì dừng lại và chuyển về màn hình chính
        if not self.analyzing:
            self.game.manager.pop()
            
            # Reset biến is_analyzing của main_scene
            self.main_scene.is_analyzing = False

            # Sử dụng lazy import để tránh partially initialized module
            from Codes.Scenes.MainGameplayScene import MainGamePlayScene
            for i in range(0, len(self.game.manager.scenes)):
                if isinstance(self.game.manager.scenes[i] , MainGamePlayScene):
                    self.game.manager.scenes[i].paused = False

    def draw(self, screen):
        # Vẽ nền: scale background only when screen size changes (cache result)
        cur_size = screen.get_size()
        # Note: scaling is done to the base (logical) size; the game will
        # later scale the whole render surface to the real window size.
        bg_rect = self._bg_orig.get_rect()
        if bg_rect.width != self.screen_width or bg_rect.height != self.screen_height:
            self._bg_scaled = pygame.transform.scale(self._bg_orig, (self.screen_width, self.screen_height))
            self._bg_scaled_size = (self.screen_width, self.screen_height)

        # Background và FA
        screen.blit(self._bg_scaled or self._bg_orig, (0, 0))
        self.fa.draw_diagram(screen, self.state_sprites)
        # Vẽ timer (góc trên bên trái)
        self._draw_timer(screen)
        # Vẽ điểm
        self.main_scene.score.draw(screen)
        #  Hiển thị progress - bao nhiêu chuỗi và chuỗi hiện tại là thứ mấy
        self._draw_progress(screen)
        # Vẽ pattern
        self._draw_pattern(screen)
    
    def _draw_timer(self, screen):
        screen_center_pos = self.game.WINDOW_WIDTH / 2
        screen_bottom_pos = self.game.WINDOW_HEIGHT - 50
        self.timer.draw(
            screen,
            x=screen_center_pos - 150,
            y=screen_bottom_pos,
            width=300,
            height=20,
            style='bar'  # hoặc 'circle', 'text'
        )
    
    def _draw_pattern(self, screen):
        DARK_ORANGE = (110, 39, 39) # RGB
        font = pygame.font.Font(None, 40)
        pattern_surf = font.render(self.current_text, True, DARK_ORANGE)
        pattern_rect = pattern_surf.get_rect(center=self.pattern_pos)
        screen.blit(pattern_surf, pattern_rect)
    
    def _draw_pattern_output(self, screen):
        YELLOW = (249, 194, 43)
        GREEN = (145, 219, 105)
        RED = (174, 35, 52)
        font = pygame.font.Font(None, 40)

        pattern_output_surf = font.render(self.fa.output, True, YELLOW)
        pattern_output_rect = pattern_output_surf.get_ret(center=(self.pattern_pos))
        screen.blit(pattern_output_surf, pattern_output_rect)

    def _draw_progress(self, screen):
        """Hiển thị text đang ở đâu trong danh sách"""
        ORANGE = (247, 150, 23)
        DARK_ORANGE = (110, 39, 39)
        WHITE = (255, 255, 255)
        font = pygame.font.Font(None, 28)
        
        # Progress text
        progress_text = f"Text {self.current_text_index + 1} / {len(self.texts)}"
        text_surf = font.render(progress_text, True, WHITE)
        
        # Vị trí: window's top-right
        top_right = (self.game.base_size[0] - 175,  50)
        text_rect = text_surf.get_rect(center=top_right)
        
        # Background
        bg_rect = text_rect.inflate(15, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(screen, (100, 200, 255), bg_rect, 2) # border
        
        screen.blit(text_surf, text_rect)
        
        # Progress bar
        bar_width = 200
        bar_height = 10
        bar_x = top_right[0] - bar_width // 2
        bar_y = top_right[1] + 20
        
        # Progress bar
        progress = (self.current_text_index + 1) / len(self.texts)
        filled_width = int(bar_width * progress)
        pygame.draw.rect(screen, ORANGE, (bar_x, bar_y, filled_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, DARK_ORANGE, (bar_x, bar_y, bar_width, bar_height), 2)

    def load_keywords(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def on_timer_timeout(self):
        '''Callback khi hết giờ'''
        print("Time's up!")
        
        #  Đánh dấu là fail
        self.main_scene.score.add_wrong()
        
        #  Chuyển sang text tiếp theo
        self.stop_analyze()
    
    def stop_analyze(self):
        """
        Dừng phân tích text hiện tại và chuyển sang text tiếp theo.
        Nếu hết text thì quay về màn hình chính.
        """
        #  Dừng timer
        self.timer.stop()

        #  Tăng index trước khi kiểm tra
        self.current_text_index += 1
        
        #  Kiểm tra xem còn text không
        if self.is_out_of_texts():
            print("All texts completed!")
            self.analyzing = False
            return
        
        #  Chuyển sang text tiếp theo
        self.current_text = self.texts[self.current_text_index]
        
        #  TẠO MỚI FA với text mới (KHÔNG dùng reset)
        self.fa = FA(self, self.current_text, self.game.base_size)
        
        #  Reset animation flags (nếu có)
        self.fa.diagram_animating = False
        self.fa.analyzing_flag = True
        
        #  Restart timer cho text mới
        self.timer.restart()

    def is_out_of_texts(self):
        """Kiểm tra xem đã hết text chưa"""
        return self.current_text_index >= len(self.texts)
    
