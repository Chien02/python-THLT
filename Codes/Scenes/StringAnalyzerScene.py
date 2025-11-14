import pygame
from Codes.Scenes.SceneBase import Scene
from Codes.Components.Automata.DFA import DFA
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

        # Draw DFA diagram based on the collided chatbox's text
        self.dfa : DFA = None
        self.diagram = None

        # Add texts from collided chatboxes
        self.texts = []
        if self.collided_chatboxes:
            for cb in self.collided_chatboxes:
                self.texts.append(cb.text)
        
        self.current_text_index = 0
        if self.texts:
            self.current_text = self.texts[self.current_text_index]
            self.draw_dfa_diagram()
        elif not self.texts and not self.collided_chatboxes:
            # Stop analyzing if no chatboxes collided (edge case)
            self.main_scene.get_string_analysis_done([])

    def handle_events(self, events):
        for event in events:
            # Handle events specific to String Analyzer Scene
            pass
        return False

    def update(self, dt):
        # Update logic for String Analyzer Scene
        pass

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
    
    def draw_dfa_diagram(self, screen):
        if not self.init_dfa():
            return False
        # Base on the dfa's transitions
        for char in self.dfa.diagram_string:
            
            screen.blit()
        pass

    def init_dfa(self):
        # Contruct a dfa based on the text M = ({states}, {characters (get from the text)}, P, start_state, [end_state])
        states = []
        for i in range(0, len(self.current_text)):
            states.append(str(i))
        
        # Characters
        characters = []
        for char in self.current_text:
            # Check for the banned characters
            if char in self.main_scene.banned_list:
                print(f"Stop analyze cause {self.current_text} has the banned character: {char}")
                return False
            characters.append(char)
        
        start_state = states[0]
        end_state = [states[-1:]]

        # Create new dfa object
        self.dfa = DFA(states, characters, start_state, end_state)
        self.dfa.init_transitions()
        return True

        
