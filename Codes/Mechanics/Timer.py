import pygame
import math

class Timer:
    """
    Countdown Timer với visualization
    - Đếm ngược từ duration về 0
    - Callback khi hết giờ
    - Visual progress bar và text
    """
    
    def __init__(self, duration=5.0, auto_start=False):
        """
        Khởi tạo Timer
        
        Args:
            duration: Thời gian đếm ngược (giây)
            auto_start: Tự động bắt đầu khi khởi tạo
        """
        self.duration = duration
        self.time_left = duration
        self.running = False
        self.paused = False
        
        # Callback khi hết giờ
        self.on_timeout = None  # Function to call when timer reaches 0
        
        # Visual settings
        self.warning_threshold = 3.0  # Cảnh báo khi còn 3s
        self.critical_threshold = 1.0  # Nguy hiểm khi còn 1s
        
        if auto_start:
            self.start()
    
    def start(self):
        """Bắt đầu/Restart timer"""
        self.time_left = self.duration
        self.running = True
        self.paused = False
    
    def stop(self):
        """Dừng timer"""
        self.running = False
        self.paused = False
    
    def pause(self):
        """Tạm dừng timer"""
        if self.running:
            self.paused = True
    
    def resume(self):
        """Tiếp tục timer"""
        if self.running:
            self.paused = False
    
    def reset(self):
        """Reset về duration ban đầu (không start)"""
        self.time_left = self.duration
        self.running = False
        self.paused = False
    
    def restart(self):
        """Reset và start lại"""
        self.reset()
        self.start()
    
    def add_time(self, seconds):
        """
        Thêm thời gian (bonus)
        
        Args:
            seconds: Số giây cần thêm
        """
        self.time_left = min(self.time_left + seconds, self.duration)
    
    def is_running(self):
        """Kiểm tra timer có đang chạy không"""
        return self.running and not self.paused
    
    def is_timeout(self):
        """Kiểm tra đã hết giờ chưa"""
        return self.time_left <= 0 and self.running
    
    def get_progress(self):
        """
        Lấy progress (0.0 - 1.0)
        
        Returns:
            float: 1.0 (đầy) → 0.0 (hết)
        """
        if self.duration <= 0:
            return 0.0
        return max(0.0, min(1.0, self.time_left / self.duration))
    
    def get_time_string(self):
        """
        Format thời gian còn lại thành string
        
        Returns:
            str: "5.0s" hoặc "0.0s"
        """
        return f"{max(0.0, self.time_left):.1f}s"
    
    def update(self, dt):
        """
        Update timer
        
        Args:
            dt: Delta time (giây)
        """
        if not self.is_running():
            return
        
        # Giảm thời gian
        self.time_left -= dt
        
        # Check timeout
        if self.time_left <= 0:
            self.time_left = 0
            self.running = False
            
            # Trigger callback
            if self.on_timeout:
                self.on_timeout()
    
    def draw(self, surface, x, y, width=300, height=30, style='bar'):
        """
        Vẽ timer lên màn hình
        
        Args:
            surface: Pygame surface
            x, y: Vị trí góc giữa bên dưới
            width, height: Kích thước
            style: 'bar' | 'circle' | 'text'
        """
        if style == 'bar':
            self._draw_bar(surface, x, y, width, height)
        elif style == 'circle':
            self._draw_circle(surface, x, y, min(width, height))
        elif style == 'text':
            self._draw_text(surface, x, y)
        else:
            self._draw_bar(surface, x, y, width, height)
    
    def _draw_bar(self, surface, x, y, width, height):
        """Vẽ timer dạng progress bar"""
        # Chọn màu dựa trên thời gian còn lại
        if self.time_left <= self.critical_threshold:
            bar_color = (255, 50, 50)    # Đỏ
            bg_color = (100, 20, 20)
            border_color = (255, 100, 100)
        elif self.time_left <= self.warning_threshold:
            bar_color = (255, 200, 0)    # Vàng
            bg_color = (100, 80, 0)
            border_color = (255, 220, 100)
        else:
            bar_color = (100, 255, 100)  # Xanh lá
            bg_color = (20, 100, 20)
            border_color = (150, 255, 150)
        
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, bg_color, bg_rect)
        
        # Progress bar
        progress = self.get_progress()
        filled_width = int(width * progress)
        if filled_width > 0:
            fill_rect = pygame.Rect(x, y, filled_width, height)
            pygame.draw.rect(surface, bar_color, fill_rect)
        
        # Border
        pygame.draw.rect(surface, border_color, bg_rect, 2)
        
        # Text (thời gian còn lại)
        font = pygame.font.Font(None, 24)
        time_text = self.get_time_string()
        text_surf = font.render(time_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(text_surf, text_rect)
        
        # Label
        # label_font = pygame.font.Font(None, 20)
        # label_surf = label_font.render("Time", True, (200, 200, 200))
        # surface.blit(label_surf, (x, y - 20))
    
    def _draw_circle(self, surface, x, y, radius):
        """Vẽ timer dạng vòng tròn (clock)"""
        center = (x + radius, y + radius)
        
        # Chọn màu
        if self.time_left <= self.critical_threshold:
            arc_color = (255, 50, 50)
            bg_color = (50, 20, 20)
        elif self.time_left <= self.warning_threshold:
            arc_color = (255, 200, 0)
            bg_color = (80, 60, 0)
        else:
            arc_color = (100, 255, 100)
            bg_color = (20, 80, 20)
        
        # Background circle
        pygame.draw.circle(surface, bg_color, center, radius)
        pygame.draw.circle(surface, arc_color, center, radius, 3)
        
        # Progress arc
        progress = self.get_progress()
        if progress > 0:
            # Vẽ arc từ 12h theo chiều kim đồng hồ
            start_angle = -math.pi / 2  # 12h
            end_angle = start_angle + (2 * math.pi * progress)
            
            # Vẽ các điểm trên arc
            points = []
            steps = max(3, int(progress * 60))
            for i in range(steps + 1):
                angle = start_angle + (end_angle - start_angle) * (i / steps)
                px = center[0] + radius * math.cos(angle)
                py = center[1] + radius * math.sin(angle)
                points.append((px, py))
            
            if len(points) >= 2:
                pygame.draw.lines(surface, arc_color, False, points, 5)
        
        # Text (thời gian)
        font = pygame.font.Font(None, 32)
        time_text = self.get_time_string()
        text_surf = font.render(time_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=center)
        surface.blit(text_surf, text_rect)
    
    def _draw_text(self, surface, x, y):
        """Vẽ timer dạng text đơn giản"""
        # Chọn màu
        if self.time_left <= self.critical_threshold:
            color = (255, 50, 50)
        elif self.time_left <= self.warning_threshold:
            color = (255, 200, 0)
        else:
            color = (100, 255, 100)
        
        # Text
        font = pygame.font.Font(None, 48)
        time_text = self.get_time_string()
        text_surf = font.render(time_text, True, color)
        text_rect = text_surf.get_rect(topleft=(x, y))
        
        # Background
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(surface, color, bg_rect, 2)
        
        surface.blit(text_surf, text_rect)


# ===== Tích hợp vào StringAnalyzerScene =====
"""
Thêm vào StringAnalyzerScene.py:

class StringAnalyzerScene(Scene):
    def __init__(self, game, main_scene, collided_chatboxes: list, background):
        super().__init__(game)
        # ... code khác ...
        
        # ✅ Khởi tạo Timer
        self.timer = Timer(duration=5.0, auto_start=False)
        self.timer.on_timeout = self.on_timer_timeout  # Set callback
        
        # Init DFA
        self.dfa = DFA(self, self.current_text)
        self.dfa.init(self.screen_width, self.screen_height)
        
        # ✅ Start timer sau khi DFA vẽ xong
        self.timer.start()
    
    def on_timer_timeout(self):
        '''Callback khi hết giờ'''
        print("⏰ Time's up!")
        
        # ✅ Đánh dấu là fail
        if hasattr(self, 'score'):
            self.score.add_wrong()
        
        # ✅ Chuyển sang text tiếp theo
        self.stop_analyze()
    
    def stop_analyze(self):
        '''Dừng phân tích và chuyển text tiếp theo'''
        # ✅ Dừng timer
        self.timer.stop()
        
        self.current_text_index += 1
        
        if self.is_out_of_texts():
            print("All texts completed!")
            self.analyzing = False
            return
        
        # Load text mới
        self.current_text = self.texts[self.current_text_index]
        self.dfa = DFA(self, self.current_text)
        self.dfa.init(self.screen_width, self.screen_height)
        self.user_input = ""
        
        # ✅ Restart timer cho text mới
        self.timer.restart()
    
    def update(self, dt):
        # ✅ Update timer
        self.timer.update(dt)
        
        # Update DFA
        self.dfa.update(dt)
        
        # Update score animation
        if hasattr(self, 'score'):
            self.score.update(dt)
    
    def draw(self, screen):
        # Vẽ background và DFA
        screen.blit(self._bg_scaled or self._bg_orig, (0, 0))
        self.dfa.draw_diagram(screen, self.state_sprites)
        
        # ✅ Vẽ timer (góc trên bên phải)
        self.timer.draw(screen, 
                       self.screen_width - 220, 20, 
                       width=200, height=30, 
                       style='bar')
        
        # Vẽ score
        if hasattr(self, 'score'):
            self.score.draw(screen, 20, 20)
"""


# # ===== DEMO =====
# if __name__ == "__main__":
#     pygame.init()
#     screen = pygame.display.set_mode((800, 600))
#     pygame.display.set_caption("Timer Demo")
#     clock = pygame.time.Clock()
    
#     # Tạo timer
#     timer = Timer(duration=10.0)
    
#     def on_timeout():
#         print("⏰ Timer finished!")
#         timer.restart()  # Auto restart cho demo
    
#     timer.on_timeout = on_timeout
#     timer.start()
    
#     running = True
#     while running:
#         dt = clock.tick(60) / 1000.0
        
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_SPACE:
#                     if timer.is_running():
#                         timer.pause()
#                         print("Paused")
#                     else:
#                         timer.resume()
#                         print("Resumed")
#                 elif event.key == pygame.K_r:
#                     timer.restart()
#                     print("Restarted")
#                 elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
#                     timer.add_time(1.0)
#                     print(f"Added 1s → {timer.get_time_string()}")
        
#         # Update
#         timer.update(dt)
        
#         # Draw
#         screen.fill((20, 20, 40))
        
#         # Vẽ timer với 3 styles khác nhau
#         timer.draw(screen, 50, 50, 300, 40, style='bar')
#         timer.draw(screen, 400, 50, 100, 100, style='circle')
#         timer.draw(screen, 300, 250, style='text')
        
#         # Instructions
#         font = pygame.font.Font(None, 24)
#         instructions = [
#             "SPACE: Pause/Resume",
#             "R: Restart",
#             "+: Add 1 second",
#             f"Status: {'Running' if timer.is_running() else 'Stopped'}",
#             f"Progress: {timer.get_progress()*100:.1f}%"
#         ]
#         for i, inst in enumerate(instructions):
#             text_surf = font.render(inst, True, (200, 200, 200))
#             screen.blit(text_surf, (50, 400 + i * 30))
        
#         pygame.display.flip()
    
#     pygame.quit()