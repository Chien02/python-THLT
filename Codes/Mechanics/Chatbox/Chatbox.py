import pygame
from Codes.Utils.TweenAnimation import Tween, Easing, EasingMode

FONT_SIZE = 32

class Chatbox:
    def __init__(self, spawner, base_sprite, text, pos, lifetime=4.0):
        from Codes.Mechanics.Chatbox.ChatboxSpawner import ChatboxSpawner
        self.spawner : ChatboxSpawner = spawner
        # States
        self.base_sprite = base_sprite
        self.holding_sprite = None
        self.interacted_sprite = None
        self.current_sprite = self.base_sprite

        self.collision_rect = pygame.Rect(pos[0], pos[1], 
                                          self.base_sprite.get_width(), 
                                          self.base_sprite.get_height())
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.text = text
        self.padding = 10
        self.text_color = "black"
        
        #  Timer và lifetime
        self.timer = 0
        self.lifetime = lifetime
        self.fade_duration = 3.0
        
        #  Alpha/opacity
        self.alpha = 255
        self.last_alpha = 255
        
        #  Position tracking
        self.current_pos = pygame.Vector2(pos[0], pos[1])
        
        #  Move animation (Tween)
        self.is_moving = False
        self.move_tween_x = None
        self.move_tween_y = None
        self.move_duration = 800.0  # 0.8 giây - mượt và dứt khoát
        
        #  Flags
        self.is_alive = True
        self.pause_fade = False  # Dừng fade khi đang di chuyển

        # Drag and drop
        self.is_dragging = False
        self.drag_offset = pygame.Vector2(0, 0)
        
        # Hàm callback gọi đến spawner khi chatbox ngủm
        self._on_chatbox_die = None

    def set_base_sprite(self, image_path):
        """Set sprite mới"""
        self.base_sprite = pygame.image.load(image_path).convert_alpha()
        self.collision_rect.size = self.base_sprite.get_size()

    def set_text(self, text):
        """Set text mới"""
        self.text = text
    
    def move_to(self, target_pos):
        """
        Di chuyển chatbox đến vị trí target với Tween animation
        
        Args:
            target_pos: tuple (x, y) hoặc pygame.Vector2
        """
        if isinstance(target_pos, (list, tuple)):
            target_pos = pygame.Vector2(target_pos[0], target_pos[1])
        
        #  Đánh dấu đang di chuyển
        self.is_moving = True
        self.pause_fade = True  # Dừng fade trong khi di chuyển
        
        #  Lấy vị trí hiện tại
        start_x = self.collision_rect.x
        start_y = self.collision_rect.y
        
        #  Tạo Tween cho X
        self.move_tween_x = Tween(
            begin=start_x,
            end=target_pos.x,
            duration=self.move_duration,
            easing=Easing.CUBIC,
            easing_mode=EasingMode.IN_OUT
        )
        self.move_tween_x.start()
        
        #  Tạo Tween cho Y
        self.move_tween_y = Tween(
            begin=start_y,
            end=target_pos.y,
            duration=self.move_duration,
            easing=Easing.CUBIC,
            easing_mode=EasingMode.IN_OUT
        )
        self.move_tween_y.start()
        
        print(f"Chatbox moving from ({start_x}, {start_y}) to ({target_pos.x}, {target_pos.y})")
    
    def handle_events(self, events, chat_num=None):
        """
        Handle mouse events cho drag and drop
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    if self.collision_rect.collidepoint(mouse_pos):
                        self._start_dragging(mouse_pos)
                        return True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.is_dragging:
                        self._stop_dragging()
                        return True
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    mouse_pos = pygame.mouse.get_pos()
                    self._drag_to(mouse_pos)
                    return True
        
        return False
    
    def _start_dragging(self, mouse_pos):
        """Bắt đầu kéo chatbox"""
        self.is_dragging = True
        self.pause_fade = True
        
        # Tính offset giữa mouse và top-left của chatbox
        self.drag_offset = pygame.Vector2(
            self.collision_rect.x - mouse_pos[0],
            self.collision_rect.y - mouse_pos[1]
        )
        
        # Dừng tween animation nếu đang chạy
        if self.is_moving:
            self.is_moving = False
            self.move_tween_x = None
            self.move_tween_y = None
        
        print(f"Started dragging chatbox at {mouse_pos}")
    
    def _drag_to(self, mouse_pos):
        """Kéo chatbox tới vị trí mới"""
        new_x = mouse_pos[0] + self.drag_offset.x
        new_y = mouse_pos[1] + self.drag_offset.y
        
        self.collision_rect.x = int(new_x)
        self.collision_rect.y = int(new_y)
        self.current_pos.x = self.collision_rect.x
        self.current_pos.y = self.collision_rect.y
    
    def _stop_dragging(self):
        """Dừng kéo chatbox"""
        self.is_dragging = False
        self.pause_fade = False
        print(f"Stopped dragging chatbox at ({self.collision_rect.x}, {self.collision_rect.y})")

    def update(self, delta_time):
        """Update timer, movement animation, và fade-out alpha"""
        
        #  Update movement tweens
        if self.is_moving and not self.is_dragging:
            if self.move_tween_x and self.move_tween_y:
                # Update tweens
                self.move_tween_x.update()
                self.move_tween_y.update()
                
                # Cập nhật vị trí từ tween
                self.collision_rect.x = int(self.move_tween_x.value)
                self.collision_rect.y = int(self.move_tween_y.value)
                self.current_pos.x = self.collision_rect.x
                self.current_pos.y = self.collision_rect.y
                
                #  Kiểm tra xem animation đã xong chưa
                if not self.move_tween_x.animating and not self.move_tween_y.animating:
                    self.is_moving = False
                    self.move_tween_x = None
                    self.move_tween_y = None
                    self.pause_fade = False  # Tiếp tục fade sau khi di chuyển xong
                    print("Chatbox reached destination")
        
        #  Update timer
        self.timer += delta_time
        
        #  Calculate alpha (chỉ khi KHÔNG đang di chuyển hoặc kéo)
        if not self.pause_fade:
            time_remaining = self.lifetime - self.timer
            if time_remaining <= self.fade_duration:
                # Fade out phase
                fade_progress = 1.0 - (time_remaining / self.fade_duration)
                self.last_alpha = int(255 * (1.0 - fade_progress))
                self.alpha = self.last_alpha
            else:
                # Still visible
                self.alpha = 255
        else:
            #  Giữ alpha ở mức hiện tại khi đang di chuyển hoặc kéo
            self.alpha = 255

    def draw(self, screen):
        """Vẽ chatbox với alpha"""
        # Set alpha trên sprite
        sprite_with_alpha = self.current_sprite.copy()
        sprite_with_alpha.set_alpha(self.alpha)
        screen.blit(sprite_with_alpha, self.collision_rect.topleft)
        
        #  Render text với word wrap
        words = self.text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.font.render(test_line, True, self.text_color)
            if test_surface.get_width() > self.collision_rect.width - 2 * self.padding:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)

        #  Vẽ text với alpha
        line_height = self.font.get_linesize()
        total_text_height = len(lines) * line_height + (len(lines) - 1) * 5
        y_start = self.collision_rect.y + (self.collision_rect.height - total_text_height) // 2
        y_offset = y_start

        for line in lines:
            text_surface = self.font.render(line, True, self.text_color)
            text_with_alpha = text_surface.copy()
            text_with_alpha.set_alpha(self.alpha)
            text_x = self.collision_rect.x + (self.collision_rect.width - text_surface.get_width()) // 2
            screen.blit(text_with_alpha, (text_x, y_offset))
            y_offset += line_height + 5

    def die(self):
        """Đánh dấu chatbox để xóa"""
        self.is_alive = False
        if self.is_moving:
            self.is_moving = False
        if self.is_dragging:
            self.is_dragging = False
        if self._on_chatbox_die:
            callback = self._on_chatbox_die
            callback()
        return self.is_alive
    
    def is_dead(self):
        """Kiểm tra xem chatbox đã chết chưa"""
        if not self.is_alive:
            return True
        
        # Chết khi hết thời gian (trừ khi đang di chuyển hoặc kéo)
        if not self.is_moving and not self.is_dragging:
            self.is_alive = self.timer < self.lifetime
        
        return not self.is_alive