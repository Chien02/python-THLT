import pygame
import json
from Codes.Scenes.SceneBase import Scene
from Codes.Components.AudioManager import AudioManager, AudioType

class Slider:
    """Component slider để điều chỉnh giá trị"""
    def __init__(self, x, y, width, height, min_val=0.0, max_val=1.0, 
                 current_val=0.5, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.label = label
        self.dragging = False
        self.handle_rect = pygame.Rect(0, 0, height, height)
        self.update_handle_pos()
    
    def update_handle_pos(self):
        """Cập nhật vị trí của slider handle"""
        ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + ratio * self.rect.width
        self.handle_rect.centery = self.rect.centery
    
    def handle_event(self, event):
        """Xử lý sự kiện chuột"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = event.pos[0]
            x = max(self.rect.x, min(x, self.rect.x + self.rect.width))
            ratio = (x - self.rect.x) / self.rect.width
            self.current_val = self.min_val + ratio * (self.max_val - self.min_val)
            self.update_handle_pos()
            return True
        return False
    
    def draw(self, screen, font, colors):
        """Vẽ slider"""
        # Vẽ track
        pygame.draw.rect(screen, colors['track'], self.rect, 2)
        
        # Vẽ handle
        pygame.draw.rect(screen, colors['handle'], self.handle_rect)
        
        # Vẽ label và giá trị
        label_surf = font.render(self.label, True, colors['text'])
        screen.blit(label_surf, (self.rect.x - 150, self.rect.y - 5))
        
        value_text = f"{int(self.current_val * 100)}%"
        value_surf = font.render(value_text, True, colors['text'])
        screen.blit(value_surf, (self.rect.x + self.rect.width + 20, self.rect.y - 5))

class SettingScene(Scene):
    def __init__(self, game, name='setting'):
        super().__init__(game, name)
        self.audio_manager: AudioManager = game.audio.audio_manager
        
        # Màu sắc
        self.colors = {
            'bg': (10, 10, 20),
            'text': (220, 220, 220),
            'title': (100, 200, 255),
            'track': (80, 80, 100),
            'handle': (200, 220, 255),
            'button': (60, 120, 200),
            'button_hover': (100, 160, 255)
        }
        
        # Fonts
        self.font_title = pygame.font.Font(None, 48)
        self.font_label = pygame.font.Font(None, 32)
        self.font_button = pygame.font.Font(None, 24)
        
        # Lấy kích thước màn hình
        self.screen_width = game.base_size[0]
        self.screen_height = game.base_size[1]
        
        # Tạo sliders
        slider_y_start = 200
        slider_spacing = 100
        
        self.music_slider = Slider(
            300, slider_y_start,
            400, 20,
            min_val=0.0, max_val=1.0,
            current_val=self.audio_manager.get_bus_volume(AudioType.MUSIC),
            label="MUSIC"
        )
        
        self.sfx_slider = Slider(
            300, slider_y_start + slider_spacing,
            400, 20,
            min_val=0.0, max_val=1.0,
            current_val=self.audio_manager.get_bus_volume(AudioType.SFX),
            label="EFFECTS"
        )
        
        self.master_slider = Slider(
            300, slider_y_start + slider_spacing * 2,
            400, 20,
            min_val=0.0, max_val=1.0,
            current_val=self.audio_manager.get_bus_volume(AudioType.MASTER),
            label="MASTER"
        )
        
        self.sliders = [self.music_slider, self.sfx_slider, self.master_slider]
        
        # Nút quay lại (góc trên trái)
        self.back_button_rect = pygame.Rect(50, 50, 80, 40)
        self.back_button_hovered = False
        
        # Nút lưu (góc dưới phải)
        self.save_button_rect = pygame.Rect(self.screen_width - 200, self.screen_height - 80, 150, 50)
        self.save_button_hovered = False
        
        # Thông báo lưu
        self.save_message = ""
        self.save_message_timer = 0.0

    def update(self, dt):
        """Cập nhật âm lượng khi slider thay đổi"""
        # Cập nhật volume cho các bus
        self.audio_manager.set_bus_volume(
            AudioType.MUSIC,
            self.music_slider.current_val
        )
        self.audio_manager.set_bus_volume(
            AudioType.SFX,
            self.sfx_slider.current_val
        )
        self.audio_manager.set_bus_volume(
            AudioType.MASTER,
            self.master_slider.current_val
        )
        
        # Cập nhật timer thông báo
        if self.save_message_timer > 0:
            self.save_message_timer -= dt
    
    def handle_events(self, events):
        """Xử lý sự kiện"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Kiểm tra nút quay lại
                if self.back_button_rect.collidepoint(event.pos):
                    # Play audio
                    self.game.audio.play_sfx('button_press')
                    self.audio_manager.save_settings()  # Tự động lưu khi thoát
                    self.game.manager.pop()
                    return True  # Quay lại scene trước
                
                # Kiểm tra nút lưu
                if self.save_button_rect.collidepoint(event.pos):
                    # Play audio
                    self.game.audio.play_sfx('button_press')
                    self.audio_manager.save_settings()
                    self.save_message = "Settings đã lưu!"
                    self.save_message_timer = 2.0
            
            # Xử lý slider events
            for slider in self.sliders:
                if slider.handle_event(event):
                    pass
            
            # Xử lý phím ESC để quay lại
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.audio_manager.save_settings()  # Tự động lưu khi thoát
                    return False
        
        return True
    
    def draw(self, screen):
        """Vẽ giao diện settings"""
        screen.fill(self.colors['bg'])
        
        # Vẽ nút quay lại
        self.back_button_hovered = self.back_button_rect.collidepoint(
            pygame.mouse.get_pos()
        )
        button_color = (self.colors['button_hover'] 
                       if self.back_button_hovered 
                       else self.colors['button'])
        pygame.draw.rect(screen, button_color, self.back_button_rect)
        pygame.draw.rect(screen, self.colors['title'], self.back_button_rect, 2)
        
        back_text = self.font_button.render("<<", True, self.colors['text'])
        back_rect = back_text.get_rect(center=self.back_button_rect.center)
        screen.blit(back_text, back_rect)
        
        # Vẽ tiêu đề
        title = self.font_title.render("SETTINGS", True, self.colors['title'])
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)
        
        # Vẽ line dưới tiêu đề
        line_y = title_rect.bottom + 20
        pygame.draw.line(
            screen, self.colors['title'],
            (200, line_y), (screen.get_width() - 200, line_y), 2
        )
        
        # Vẽ sliders
        for slider in self.sliders:
            slider.draw(screen, self.font_label, self.colors)
        
        # Vẽ nút lưu
        self.save_button_hovered = self.save_button_rect.collidepoint(
            pygame.mouse.get_pos()
        )
        save_color = (self.colors['button_hover'] 
                     if self.save_button_hovered 
                     else self.colors['button'])
        pygame.draw.rect(screen, save_color, self.save_button_rect)
        pygame.draw.rect(screen, self.colors['title'], self.save_button_rect, 2)
        
        save_text = self.font_button.render("SAVE", True, self.colors['text'])
        save_rect = save_text.get_rect(center=self.save_button_rect.center)
        screen.blit(save_text, save_rect)
        
        # Vẽ thông báo lưu
        if self.save_message_timer > 0:
            msg_surf = self.font_button.render(
                self.save_message, True, (100, 255, 100)
            )
            msg_rect = msg_surf.get_rect(
                center=(screen.get_width() // 2, 
                       screen.get_height() - 80)
            )
            screen.blit(msg_surf, msg_rect)