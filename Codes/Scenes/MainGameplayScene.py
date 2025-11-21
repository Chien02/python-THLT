import pygame

from Codes.Scenes.PauseMenuScene import PauseMenuScene
from Codes.Scenes.SceneBase import Scene
from Codes.Scenes.UILayerScene import UILayerScene
from Codes.Scenes.GameOverScene import GameOverScene
from Codes.Scenes.StringAnalyzerScene import StringAnalyzerScene
from Codes.Mechanics.Chatbox.ChatboxSpawner import ChatboxSpawner
from Codes.Mechanics.WordGenerator.BannedListGenerator import BannedListGenerator
from Codes.Mechanics.Score import Score
from Codes.Entities.Machine.Machine import Machine


class MainGamePlayScene(Scene):
    def __init__(self, game, name='main_game'):
        super().__init__(game, name)

        # Lưu kích thước màn hình (lấy từ game)
        # Lưu kích thước màn hình logic (base size defined by Game)
        self.screen_width, self.screen_height = game.base_size

        # --- Load assets ---
        # Keep the original background so we can rescale it when the window size changes
        self._bg_orig = pygame.image.load("Assets/Images/Backgrounds/BiggerBackground.png").convert()
        self._bg_scaled = None
        self._bg_scaled_size = None

        # Machine Animation
        machine_pos = (360, 240)
        self.machine = Machine(machine_pos)

        # Chatbox Spawner
        self.chatbox_spawner = ChatboxSpawner(spawn_interval=4.0, chatbox_lifetime=5.0, machine_pos=machine_pos)

        # Analysize section
        self.is_analyzing = False
        self.analyzing_background = pygame.image.load("Assets/Images/Backgrounds/AnalyzingBackground.png").convert()

        # Banned List
        self.num_of_banned = 5
        self.banned_generator = BannedListGenerator()
        self.banned_list = self.banned_generator.generate(self.num_of_banned)

        # Khởi tạo Score Manager
        self.score : Score = self.game.score

        # Các collided chatboxes được ghi lại, do phải đợi animation thực hiện xong
        self.pending_collisions = None

    def handle_events(self, events):
        for event in events:
            if self.chatbox_spawner.handle_events([event]): return True
            if self.machine.handle_events([event]): return True

            # Thêm pause menu scene
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not isinstance(self.game.manager.top(), PauseMenuScene):
                        self.game.manager.push(PauseMenuScene(self.game, 'pause'))
                        # Tạm dừng main scene
                        self.paused = True
                        return True
        return False

    def update(self, dt):
        if self.score:
            self.score.update(dt)
        
        self.machine.update(dt)
        self.chatbox_spawner.update(dt)
        # Collision: let the machine check against current chatboxes
        collided = self.machine.collide_with_chatboxes(self.chatbox_spawner.chatboxes)
        
        if collided:
            # Flag này dùng để kiểm tra xem nên chơi anim cry or happy -- Cập nhật bằng state machine sau
            is_happy = True

            self.machine.stretch()
            # Check for banned characters
            total_wrong_attemp = 0
            for coll in collided[:]:
                if self.banned_generator.is_in_banned_list(coll.text):
                    total_wrong_attemp += 1
                    dmg = 20
                    self.machine.health.take_damage(dmg)
                    collided.remove(coll)
                    is_happy = False

            # Kiểm tra trước xem có dead chưa, dead trước khi analyze
            if not self.machine.health.is_alive():
                self.machine.sprite_frames.play('over', loop=False)
                self.machine._waiting_for_animaiton = True
                self.machine._on_animation_complete = self._on_machine_die
                return

            # Thực hiện animation tùy thuộc vào flag is_happy
            if is_happy:
                self.machine.sprite_frames.play('happy', loop=False)
                self.machine._waiting_for_animaiton = True
            else:
                self.machine.sprite_frames.play('cry', loop=False)
                self.machine._waiting_for_animaiton = True
            
            # Stop the thing and subtract the scores
            if total_wrong_attemp > 0:
                # For FX: Shake the screen
                self.score.add_wrong(attemp=total_wrong_attemp)
            
        # One more check after remove the chatboxes that have banned characters
        if collided and self.is_analyzing == False:
            self.pending_collisions = collided

            # Set callback function for animation completion
            self.machine._on_animation_complete = self._on_machine_animation_complete


    def _on_machine_animation_complete(self):
        if self.pending_collisions and not isinstance(self.game.manager.top(), StringAnalyzerScene):
            self.is_analyzing = True
            self.game.manager.push(StringAnalyzerScene(self.game,self, self.pending_collisions, self.analyzing_background))
            
            # Make sure to clear it after it done
            self.pending_collisions = None
            # Thêm scene vào và đổi vị trí
            """
                Analyzer      -->   Analyzer + Buttons
                UI Scene      -->   UI Scene
                MainGameplay  -->   MainGameplay
            """
            for i in range(0, len(self.game.manager.scenes)):
                if isinstance(self.game.manager.scenes[i] , MainGamePlayScene):
                    self.game.manager.scenes[i].paused = True
    
    def _on_machine_die(self):
        if not isinstance(self.game.manager.top(), GameOverScene):
            self.game.manager.push(GameOverScene(self.game, 'game_over'))
            # Tạm dừng main scene
            self.paused = True


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
