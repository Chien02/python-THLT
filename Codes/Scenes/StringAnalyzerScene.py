import pygame
import json
from Codes.Scenes.SceneBase import Scene
from Codes.Components.Automata.DFA import DFA
from Codes.Mechanics.WordGenerator.BannedListGenerator import BannedListGenerator
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.TweenAnimation import TweenAnimation

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

        # Init_DFA based on text
        self.dfa : DFA = DFA(self, self.current_text)
        self.dfa.init()

        if self.current_text:
            self.analyzing = True
        else:
            self.analyzing = False

    def handle_events(self, events):
        for event in events:
            # Handle events specific to String Analyzer Scene
            return self.dfa.handle_events([event])
        return False

    def update(self, dt):
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

    def load_keywords(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def stop_analyze(self):
        self.analyzing = False

        
