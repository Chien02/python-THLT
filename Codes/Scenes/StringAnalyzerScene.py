import pygame
import json
from Codes.Scenes.SceneBase import Scene
from Codes.Components.Automata.DFA import DFA
from Codes.Mechanics.WordGenerator.BannedListGenerator import BannedListGenerator
from Codes.Mechanics.Timer import Timer
from Codes.Utils.FrameLoader import FrameLoader

class StringAnalyzerScene(Scene):
    def __init__(self, game, main_scene, collided_chatboxes: list, background):
        super().__init__(game)
        self.main_scene = main_scene
        self.collided_chatboxes = collided_chatboxes
        self._bg_orig = background

        self.screen_width, self.screen_height = game.base_size
        self._bg_scaled = None
        self._bg_scaled_size = None

        # Load assets
        frame_size = (90, 90)
        self.state_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Diagram/circles.png", frame_size[0], frame_size[1], 3)
        self.arrow_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Diagram/arrows.png", frame_size[0], frame_size[1], 3)

        # Add texts from collided chatboxes
        self.texts = []
        if self.collided_chatboxes:
            for cb in self.collided_chatboxes:
                self.texts.append(cb.text)
        
        self.current_text_index = 0
        if self.texts:
            self.current_text = self.texts[self.current_text_index]
        
        # keywords
        self.keywords = self.load_keywords("Data/keywords.json")["keywords"]
        # Banned List
        self.num_of_banned = 5
        self.banned_list = BannedListGenerator.generate(self.num_of_banned, self.num_of_banned)

        # Init Timer
        self.timer = Timer(duration=5.0, auto_start=False)
        self.timer.on_timeout = self.on_timer_timeout  # Set callback

        # Init_DFA based on text
        self.dfa : DFA = DFA(self, self.current_text)
        self.dfa.init()

        # Dừng lại khi xử lý hết chatbox được truyền vào:
        if self.current_text_index != len(self.texts):
            self.analyzing = True
        else:
            self.analyzing = False
        
        #  Start timer sau khi DFA vẽ xong
        self.timer.start()

    def handle_events(self, events):
        for event in events:
            # Handle events specific to String Analyzer Scene
            return self.dfa.handle_events([event])
        return False

    def update(self, dt):
        # Update timer
        self.timer.update(dt)

        self.dfa.update(dt)
        # Nếu ngưng analyzing thì dừng lại và chuyển về màn hình chính
        if not self.analyzing:
            self.game.manager.pop()
            # Sử dụng lazy import để tránh partially initialized module
            from Codes.Scenes.MainGameplayScene import MainGamePlayScene
            if isinstance(self.game.manager.scenes[-2], MainGamePlayScene):
                self.game.manager.scenes[-2].paused = False

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
        
        self.dfa.draw_diagram(screen, self.state_sprites)

        """ Vẽ timer"""
        # Background và DFA
        screen.blit(self._bg_scaled or self._bg_orig, (0, 0))
        self.dfa.draw_diagram(screen, self.state_sprites)
        
        # Vẽ timer (góc trên bên trái)
        self.timer.draw(
            screen,
            x=0 + 20,
            y=20,
            width=200,
            height=30,
            style='bar'  # hoặc 'circle', 'text'
        )

        #  Hiển thị progress
        self._draw_progress(screen)
    
    def _draw_progress(self, screen):
        """Hiển thị text đang ở đâu trong danh sách"""
        font = pygame.font.Font(None, 28)
        ORANGE = (247, 150, 23)
        DARK_ORANGE = (110, 39, 39)
        
        # Progress text
        progress_text = f"Text {self.current_text_index + 1} / {len(self.texts)}"
        text_surf = font.render(progress_text, True, (255, 255, 255))
        
        # Vị trí: Góc trên bên phải
        text_rect = text_surf.get_rect(topright=(self.screen_width - 20, 20))
        
        # Background
        bg_rect = text_rect.inflate(15, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(screen, (100, 200, 255), bg_rect, 2)
        
        screen.blit(text_surf, text_rect)
        
        # Progress bar
        bar_width = 200
        bar_height = 10
        bar_x = self.screen_width - bar_width - 20
        bar_y = 55
        
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
        
        # #  Đánh dấu là fail
        # if hasattr(self, 'score'):
        #     self.score.add_wrong()
        
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
        
        #  TẠO MỚI DFA với text mới (KHÔNG dùng reset)
        self.dfa = DFA(self, self.current_text)
        self.dfa.init()
        
        #  Reset animation flags (nếu có)
        self.dfa.diagram_animating = False
        self.dfa.analyzing_flag = True
        
        #  Restart timer cho text mới
        self.timer.restart()

    def is_out_of_texts(self):
        """Kiểm tra xem đã hết text chưa"""
        return self.current_text_index >= len(self.texts)
        
