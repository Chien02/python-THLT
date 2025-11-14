import pygame

FONT_SIZE = 24
class Chatbox:
    def __init__(self, base_sprite, text, pos, lifetime=4.0):
        # States
        self.base_sprite = base_sprite
        self.holding_sprite = None
        self.interacted_sprite = None
        self.current_sprite = self.base_sprite

        self.collision_rect = pygame.Rect(pos[0], pos[1], self.base_sprite.get_width(), self.base_sprite.get_height())
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.text = text
        self.padding = 10
        self.text_color = "black"
        self.timer = 0
        self.lifetime = lifetime  # seconds
        self.fade_duration = 3.0  # Fade out over 3 seconds before disappearing
        
        # Alpha/opacity for fade-out
        self.alpha = 255  # Full opacity (0-255)
        
        # Drag attributes
        self.is_dragging = False
        self.can_drag = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Interpolation attributes
        self.target_pos = pygame.Vector2(pos[0], pos[1])
        self.smooth_speed = 0.2  # lower = smoother, 0.2–0.3 is good

        # Disappear flag
        self.is_alive = True

    def set_base_sprite(self, image_path):
        self.base_sprite = pygame.image.load(image_path).convert_alpha()
        self.collision_rect.size = self.base_sprite.get_size()

    def set_text(self, text):
        self.text = text

    def handle_events(self, events, chat_num = None):
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Left button

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.collision_rect.collidepoint(event.pos):
                    self.can_drag = True
                    self.drag_offset_x = event.pos[0] - self.collision_rect.x
                    self.drag_offset_y = event.pos[1] - self.collision_rect.y
                    return True

            elif event.type == pygame.MOUSEBUTTONUP:
                self.is_dragging = False
                self.can_drag = False
                self.current_sprite = self.base_sprite
                return True

            elif event.type == pygame.MOUSEMOTION:
                if self.collision_rect.collidepoint(event.pos):
                    self.interacted_sprite = pygame.image.load("Assets/Images/Elements/Chatbox/chatbox_interact" + str(chat_num + 1) + ".png").convert_alpha()
                    self.current_sprite = self.interacted_sprite
                else:
                    self.current_sprite = self.base_sprite

                    # Kích hoạt dragging thật sự
                if self.can_drag and mouse_pressed:
                    self.is_dragging = True
                    self.holding_sprite = pygame.image.load("Assets/Images/Elements/Chatbox/chatbox_holding" + str(chat_num + 1) + ".png").convert_alpha()
                    self.current_sprite = self.holding_sprite
                else:
                    self.is_dragging = False
                
                if self.is_dragging:
                    # Cập nhật vị trí mục tiêu (target position)
                    self.target_pos.x = event.pos[0] - self.drag_offset_x
                    self.target_pos.y = event.pos[1] - self.drag_offset_y
                    return True
        return False
    

    def update(self, delta_time):
        """Update timer, smooth movement, and calculate fade-out alpha."""
        self.timer += delta_time
        
        # Calculate alpha based on remaining time (fade out over last fade_duration seconds)
        time_remaining = self.lifetime - self.timer
        if time_remaining <= self.fade_duration:
            # In fade-out phase: lerp alpha from 255 to 0
            fade_progress = 1.0 - (time_remaining / self.fade_duration)  # 0 to 1
            self.alpha = int(255 * (1.0 - fade_progress))
        else:
            # Still visible
            self.alpha = 255
        
        # Smoothly move the chatbox toward target position
        current_pos = pygame.Vector2(self.collision_rect.topleft)
        # Nội suy tuyến tính (lerp)
        alpha = 1 - pow(1 - self.smooth_speed, delta_time * 60)
        new_pos = current_pos.lerp(self.target_pos, alpha)
        self.collision_rect.topleft = (round(new_pos.x), round(new_pos.y))


    def draw(self, screen):
        # Set alpha on the current sprite and draw background
        sprite_with_alpha = self.current_sprite.copy()
        sprite_with_alpha.set_alpha(self.alpha)
        screen.blit(sprite_with_alpha, self.collision_rect.topleft)
        
        # Render text with alpha
        words = self.text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.font.render(test_line, True, self.text_color)
            if test_surface.get_width() > self.collision_rect.width - 2 * self.padding:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        lines.append(current_line)

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
        self.is_alive = False
        return self.is_alive
    
    def is_dead(self):
        if self.is_alive is False:
            return True
        self.is_alive = self.timer < self.lifetime
        return not self.is_alive