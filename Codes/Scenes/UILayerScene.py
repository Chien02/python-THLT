
import pygame
from Codes.Scenes.SceneBase import Scene
from Codes.Scenes.PauseMenuScene import PauseMenuScene
from Codes.Mechanics.WordGenerator.BannedListGenerator import BannedListGenerator
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Components.Buttons import *

class UILayerScene(Scene):
    def __init__(self, game, name='ui'):
        super().__init__(game, name)

        # Pause button
        small_btn_size = (48, 48)
        offset_x = small_btn_size[0] + (small_btn_size[0]//4)
        offset_y = 50
        pause_btn_pos_x = self.game.base_size[0] - offset_x
        pause_btn_pos_y = 50

        # self.pause_button = ButtonWithImage(pause_btn_pos_x, pause_btn_pos_y, "Assets/Images/UIs/Buttons/pauseButton.png")
        sprites = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Buttons/pause_small.png", small_btn_size[0], small_btn_size[1], 3)
        self.pause_button = ButtonWithSprites(pause_btn_pos_x, pause_btn_pos_y, sprites=sprites)
        self.pause_button._on_pressed = self._on_pause_button_pressed
        
        #region Banned List Sprites
        # Banned list sprite
        self.banned_list_sprite = pygame.image.load("Assets/Images/Elements/Banned_list/banned_list_rect.png").convert_alpha()
        self.banned_list_decor_sprite = pygame.image.load("Assets/Images/Elements/Banned_list/banned_list_decor.png").convert_alpha()
        self.banned_list_rect = self.banned_list_sprite.get_rect()
        self.banned_list_decor_rect = self.banned_list_decor_sprite.get_rect()
        
        #  Vị trí bảng (góc phải màn hình)
        self.banned_list_pos = (game.base_size[0] - self.banned_list_rect.width - 20, 
                                (((game.base_size[1] - self.banned_list_rect.height) // 2) + (self.banned_list_rect.height // 6)))
        #  vị trí của hình trang trí, nằm ngay góc trên bên trái của bảng
        move_to_topleft_dist = 70
        self.decor_pos = (self.banned_list_pos[0] - move_to_topleft_dist, self.banned_list_pos[1] - move_to_topleft_dist)
        
        #endregion

        #  Lấy reference đến main scene
        self.main_scene = self.game.main_scene
        
        #  Banned list data
        self.banned_list = []
        
        #  Visual settings
        self.font_size = 24
        self.font = pygame.font.Font(None, self.font_size)
        self.margin = 50
        self.cell_padding =  5 # Khoảng cách giữa các ô
        self.text_color = (50, 50, 50)  # Màu chữ
        self.banned_color = (200, 50, 50)  # Màu đỏ cho ký tự bị cấm
        # Bảng con --> Nội dung được vẽ bên trong bảng con
        self.sub_banned_rect = pygame.Rect(self.banned_list_pos, 
                                           (self.banned_list_rect.width - self.margin, self.banned_list_rect.height - self.margin))
            
    def update(self, dt):
        #  Tìm main scene nếu chưa có
        if self.main_scene is None:
            self._find_main_scene()
        
        #  Update banned list từ main scene
        if self.main_scene and hasattr(self.main_scene, 'banned_list'):
            if self.banned_list != self.main_scene.banned_list:
                self.update_banned_list(self.main_scene.banned_list)
    
    def update_banned_list(self, new_banned_list):
        """Cập nhật banned list"""
        self.banned_list = new_banned_list
        print(f"Banned list updated: {self.banned_list}")
    

    def handle_events(self, events):
        for event in events:
            if self.pause_button.handle_events([event]):
                return True
        return False

    def _on_pause_button_pressed(self):
        # Play audio
        self.game.audio.play_sfx('button_press')
        # Thêm pause menu scene
        if not isinstance(self.game.manager.top(), PauseMenuScene):
            self.game.manager.push(PauseMenuScene(self.game))
            # Tạm dừng main scene
            if self.main_scene:
                self.main_scene.paused = True
        return True

    def draw(self, screen):
        """Vẽ UI layer"""
        # Vẽ hình decor do muốn hình này bị đè bởi bảng
        screen.blit(self.banned_list_decor_sprite, self.decor_pos)

        #  Vẽ background bảng banned list
        screen.blit(self.banned_list_sprite, self.banned_list_pos)
        
        #  Vẽ các ký tự bị banned
        if self.banned_list:
            self._draw_banned_characters(screen)

        #  Vẽ pause button
        self.pause_button.draw(screen)
    
    def _draw_banned_characters(self, screen):
        """
        Vẽ các ký tự trong banned list lên bảng
        Layout: Grid với 4 cột, tự động wrap xuống dòng mới
        """
        #  Cấu hình grid
        columns = 3  # Số cột
        cell_width = self.sub_banned_rect.width // columns
        cell_height = self.font_size + self.cell_padding * 2
        
        #  Vị trí bắt đầu (góc trên trái của bảng)
        #  Sử dụng bảng con phía bên trong thay vì bảng lớn
        horizontal_offset = 25
        vertical_offset = 50
        start_x = self.banned_list_pos[0] + horizontal_offset # Offset từ trái bảng (để tránh động chạm cạnh bảng)
        start_y = self.banned_list_pos[1] + vertical_offset  # Offset từ đầu bảng (để tránh title)
        
        #  Vẽ từng ký tự
        for i, char in enumerate(self.banned_list):
            # Tính vị trí hàng và cột
            row = i // columns
            col = i % columns
            
            # Tính tọa độ trung tâm của ô
            cell_x = start_x + col * cell_width + cell_width // 2
            cell_y = start_y + row * cell_height + cell_height // 2
            
            #  Vẽ background cho ô (optional)
            cell_rect = pygame.Rect(
                start_x + col * cell_width + 10, # Left margin
                start_y + row * cell_height + 5,
                cell_width - 20, # Right margin
                cell_height - 10
            )
            pygame.draw.rect(screen, (255, 255, 255, 100), cell_rect)
            pygame.draw.rect(screen, self.banned_color, cell_rect, 2) # border
            
            #  Vẽ ký tự
            char_surf = self.font.render(str(char).upper(), True, self.banned_color)
            char_rect = char_surf.get_rect(center=(cell_x, cell_y))
            screen.blit(char_surf, char_rect)
    
    def _draw_banned_characters_alternative(self, screen):
        """
         Alternative layout: Vẽ theo vertical list
        (Dùng nếu muốn layout dọc thay vì grid)
        """
        start_x = self.banned_list_pos[0] + 20
        start_y = self.banned_list_pos[1] + 50
        spacing = 40  # Khoảng cách giữa các ký tự
        
        for i, char in enumerate(self.banned_list):
            y = start_y + i * spacing
            
            # Vẽ bullet point
            pygame.draw.circle(screen, self.banned_color, (start_x, y), 5)
            
            # Vẽ ký tự
            char_surf = self.font.render(f" {str(char).upper()}", True, self.text_color)
            screen.blit(char_surf, (start_x + 15, y - self.font_size // 2))
    
    def _draw_banned_characters_fancy(self, screen):
        """
        Fancy layout: Với icon X và styling đẹp hơn
        """
        columns = 4
        cell_width = self.sub_banned_rect.width // columns
        cell_height = 45
        
        start_x = self.banned_list_pos[0]
        start_y = self.banned_list_pos[1] + 60
        
        for i, char in enumerate(self.banned_list):
            row = i // columns
            col = i % columns
            
            cell_x = start_x + col * cell_width + cell_width // 2
            cell_y = start_y + row * cell_height + cell_height // 2
            
            #  Vẽ circle background
            pygame.draw.circle(screen, (255, 200, 200), (cell_x, cell_y), 18)
            pygame.draw.circle(screen, self.banned_color, (cell_x, cell_y), 18, 2)
            
            #  Vẽ X icon nhỏ (banned symbol)
            x_size = 5
            x_offset = 10
            pygame.draw.line(screen, (200, 0, 0), 
                           (cell_x - x_size + x_offset, cell_y - x_size), 
                           (cell_x + x_size + x_offset, cell_y + x_size), 2)
            pygame.draw.line(screen, (200, 0, 0), 
                           (cell_x - x_size + x_offset, cell_y + x_size), 
                           (cell_x + x_size + x_offset, cell_y - x_size), 2)
            
            #  Vẽ ký tự
            char_surf = self.font.render(str(char).upper(), True, self.banned_color)
            char_rect = char_surf.get_rect(center=(cell_x - 5, cell_y))
            screen.blit(char_surf, char_rect)
    
    def _draw_title(self, screen):
        """Vẽ title cho bảng (optional)"""
        title_font = pygame.font.Font(None, 28)
        title_surf = title_font.render("BANNED LETTERS", True, (200, 50, 50))
        title_rect = title_surf.get_rect(
            centerx=self.banned_list_pos[0] + self.banned_list_rect.width // 2,
            y=self.banned_list_pos[1] + 15
        )
        screen.blit(title_surf, title_rect)
        