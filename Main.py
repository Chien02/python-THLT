import pygame, sys


# from pygame.locals import * # Import game's modules
from Codes.SceneManager import SceneManager
from Codes.Scenes.MainGameplayScene import MainGamePlayScene 
from Codes.Scenes.PauseMenuScene import PauseMenuScene
from Codes.Components.Buttons import Button

class Game:
# ---- Variables ------
# UI's properties
    def __init__(self):
        SCALED_RATIO = 4
        WINDOW_WIDTH = 800
        WINDOW_HEIGHT = 600
        self.window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.game_title = "Langua Machine Game"
        self.clock = pygame.time.Clock() # This is important
        self.delta_time = 0.85
        self.running = True

        # INIT PYGAME
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size, 0, 32)
        pygame.display.set_caption(f"{self.game_title}")

    def run(self):
        # Init classes
        manager = SceneManager(self)
        main_gameplay_scene = MainGamePlayScene(self)
        # pause_scene = PauseMenuScene(self)
        # pause_button = Button(self, 300, 400, 200, 50, (0, 100, 200), "PAUSE")

        # Add all the scenes to manager
        manager.push(main_gameplay_scene)
        # manager.push(pause_scene)

        # ----- Game Loop ------
        while self.running:
            # Maintain 60 fps
            self.clock.tick(60)
            delta_time = self.clock.get_time() / 1000.0 # in seconds

            # Collect events once and reuse them
            events = pygame.event.get()

            # Run the scene manager's frame with captured events
            manager.run_frame(delta_time, events, self.screen)

            # Handle top-level events (like window close) using same list
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

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