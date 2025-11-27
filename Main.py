import pygame, sys
import json
import asyncio

from Codes.Utils.SceneManager import SceneManager
from Codes.Scenes.MainMenu import MainMenuScene
from Codes.Scenes.MainGameplayScene import MainGamePlayScene
from Codes.Scenes.PauseMenuScene import PauseMenuScene
from Codes.Scenes.UILayerScene import UILayerScene
from Codes.Mechanics.Score import Score
from Codes.Components.Audio import Audio

class Game:
    SCALED_RATIO = 4
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768

    def __init__(self):
        self.base_size = (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.window_size = (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.game_title = "Langua Machine Game"
        self.clock = pygame.time.Clock()
        self.delta_time = 0.85
        self.running = True

        self.manager = SceneManager(self)
        self.main_scene = None
        self.render_surface = pygame.Surface(self.base_size)
        self.score = None
        self.audio = Audio()

        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE, 32)
        pygame.display.set_caption(f"{self.game_title}")

    async def run(self):
        self.score = Score(
            correct_points=10,
            wrong_points=-10,
            combo_multiplier=1.5
        )
        self.main_menu_scene = MainMenuScene(self, 'main_menu')
        self.main_scene = None
        self.manager.push(self.main_menu_scene)

        while self.running:
            self.clock.tick(60)
            delta_time = self.clock.get_time() / 1000.0

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.VIDEORESIZE:
                    self.window_size = event.size
                    self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE, 32)

            scale_x = self.window_size[0] / self.base_size[0]
            scale_y = self.window_size[1] / self.base_size[1]

            remapped_events = []
            for event in events:
                try:
                    ed = event.dict.copy()
                except Exception:
                    ed = {}
                if 'pos' in ed and ed['pos'] is not None:
                    px, py = ed['pos']
                    ed['pos'] = (int(px / scale_x), int(py / scale_y))
                try:
                    new_event = pygame.event.Event(event.type, ed)
                    remapped_events.append(new_event)
                except Exception:
                    remapped_events.append(event)

            if self.score.combo == 1 or self.score.combo == 5:
                self.audio.play_sfx('collect')
            self.render_surface.fill((0, 0, 0))
            self.manager.run_frame(delta_time, remapped_events, self.render_surface)

            try:
                scaled = pygame.transform.smoothscale(self.render_surface, self.window_size)
            except Exception:
                scaled = pygame.transform.scale(self.render_surface, self.window_size)
            self.screen.blit(scaled, (0, 0))

            pygame.display.flip()
            
            # Yield to event loop
            await asyncio.sleep(0)

        pygame.quit()
        sys.exit()

    def _on_reload_main_scene(self):
        self.score = Score(
            correct_points=10,
            wrong_points=-10,
            combo_multiplier=1.5
        )
        new_scene = MainGamePlayScene(self)
        self.main_scene = new_scene
        new_ui_scene = UILayerScene(self)
        
        self.manager.replace(new_scene.name, new_scene)
        self.manager.replace(new_ui_scene.name, new_ui_scene)


async def main():
    try:
        game = Game()
        await game.run()
    except Exception:
        import traceback
        traceback.print_exc()
        try:
            input("Press ENTER to exit")
        except Exception:
            pass


# Entry point
if __name__ == "__main__":
    asyncio.run(main())