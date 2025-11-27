import pygame, sys
import json


# from pygame.locals import * # Import game's modules
from Codes.Utils.SceneManager import SceneManager
from Codes.Scenes.MainMenu import MainMenuScene
from Codes.Scenes.MainGameplayScene import MainGamePlayScene
from Codes.Scenes.PauseMenuScene import PauseMenuScene
from Codes.Scenes.UILayerScene import UILayerScene
from Codes.Mechanics.Score import Score
from Codes.Components.Audio import Audio

class Game:
# ---- Variables ------
    SCALED_RATIO = 4
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768
# UI's properties
    def __init__(self):
        # base (logical) resolution everything is laid out in
        self.base_size = (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        # actual window size (may differ when user resizes)
        self.window_size = (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.game_title = "Langua Machine Game"
        self.clock = pygame.time.Clock() # This is important
        self.delta_time = 0.85
        self.running = True

        # scene manager
        self.manager = SceneManager(self)
        self.main_scene = None

        # a render target at the base logical resolution; scenes draw here
        self.render_surface = pygame.Surface(self.base_size)

        # score manager
        self.score : Score = None

        # audio
        self.audio = Audio()

        # INIT PYGAME
        pygame.init()
        # Make the window resizable so the background can adapt to new sizes
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE, 32)
        pygame.display.set_caption(f"{self.game_title}")

    def run(self):
        # Khởi tạo Score Manager
        self.score = Score(
            correct_points=10,      # +10 điểm khi đúng
            wrong_points=-10,        # -5 điểm khi sai
            combo_multiplier=1.5    # Nhân 1.5x khi combo >= 5
        )
        # Init scenes
        self.main_menu_scene = MainMenuScene(self, 'main_menu')
        self.main_scene = None

        # Add all the scenes to manager
        self.manager.push(self.main_menu_scene)

        # ----- Game Loop ------
        while self.running:
            # Maintain 60 fps
            self.clock.tick(60)
            delta_time = self.clock.get_time() / 1000.0 # in seconds

            # Collect events once and reuse them
            events = pygame.event.get()

            # Handle window resize events first so we can update the display surface
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.VIDEORESIZE:
                    self.window_size = event.size
                    self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE, 32)

            # Compute scale from base -> window so we can remap input coordinates
            scale_x = self.window_size[0] / self.base_size[0]
            scale_y = self.window_size[1] / self.base_size[1]

            # Remap mouse positions in events to base (logical) coordinates for scenes
            remapped_events = []
            for event in events:
                # copy event attributes and remap 'pos' if present
                try:
                    ed = event.dict.copy()
                except Exception:
                    ed = {}
                if 'pos' in ed and ed['pos'] is not None:
                    px, py = ed['pos']
                    ed['pos'] = (int(px / scale_x), int(py / scale_y))
                # Build a new event using the possibly-updated dict; fallback to original event if creation fails
                try:
                    new_event = pygame.event.Event(event.type, ed)
                    remapped_events.append(new_event)
                except Exception:
                    remapped_events.append(event)

            # Run the scene manager's frame drawing to the base render surface
            if self.score.combo == 1 or self.score.combo == 5:
                self.audio.play_sfx('collect')
            self.render_surface.fill((0,0,0))
            self.manager.run_frame(delta_time, remapped_events, self.render_surface)

            # Scale the render surface to the actual window and blit
            try:
                scaled = pygame.transform.smoothscale(self.render_surface, self.window_size)
            except Exception:
                scaled = pygame.transform.scale(self.render_surface, self.window_size)
            self.screen.blit(scaled, (0,0))

            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def _on_reload_main_scene(self):
        # Reload score
        self.score = Score(
            correct_points=10,      # +10 điểm khi đúng
            wrong_points=-10,        # -5 điểm khi sai
            combo_multiplier=1.5    # Nhân 1.5x khi combo >= 5
        )
        new_scene = MainGamePlayScene(self)
        self.main_scene = new_scene
        new_ui_scene = UILayerScene(self)
        
        self.manager.replace(new_scene.name, new_scene)
        self.manager.replace(new_ui_scene.name, new_ui_scene)


if __name__ == "__main__":
    # Wrap execution so we print a full traceback to the console
    try:
        Game().run()
    except Exception:
        import traceback
        traceback.print_exc()
        # Pause so the console stays open when run from double-click or some terminals
        try:
            input("Press ENTER to exit")
        except Exception:
            pass