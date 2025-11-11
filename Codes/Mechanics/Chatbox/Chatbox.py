import pygame

class Chatbox:
    def __init__(self, pos_x, pos_y, font_size=24):
        self.base_sprite = pygame.image.load("Assets/Images/Elements/Chatbox/Chatbox1.png").convert_alpha()
        self.collision_rect = pygame.Rect(pos_x, pos_y, self.base_sprite.get_width(), self.base_sprite.get_height())
        self.font = pygame.font.Font(None, font_size)
        self.text = ""
        self.padding = 10
        self.text_color = "black"
        
        # Drag attributes
        self.is_dragging = False
        self.can_drag = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Interpolation attributes
        self.target_pos = pygame.Vector2(pos_x, pos_y)
        self.smooth_speed = 0.2  # lower = smoother, 0.2–0.3 is good

    def set_base_sprite(self, image_path):
        self.base_sprite = pygame.image.load(image_path).convert_alpha()
        self.collision_rect.size = self.base_sprite.get_size()

    def set_text(self, text):
        self.text = text

    def handle_events(self, events):
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
                return True

            elif event.type == pygame.MOUSEMOTION:
                    # Kích hoạt dragging thật sự
                if self.can_drag and mouse_pressed:
                    self.is_dragging = True
                else:
                    self.is_dragging = False
                
                if self.is_dragging:
                    # Cập nhật vị trí mục tiêu (target position)
                    self.target_pos.x = event.pos[0] - self.drag_offset_x
                    self.target_pos.y = event.pos[1] - self.drag_offset_y
                    return True

        return False

    def update(self, delta_time):
        """Smoothly move the chatbox toward target position."""
        current_pos = pygame.Vector2(self.collision_rect.topleft)
        # Nội suy tuyến tính (lerp)

        alpha = 1 - pow(1 - self.smooth_speed, delta_time * 60)
        new_pos = current_pos.lerp(self.target_pos, alpha)

        self.collision_rect.topleft = (round(new_pos.x), round(new_pos.y))

    def draw(self, screen):
        # Draw background
        screen.blit(self.base_sprite, self.collision_rect.topleft)
        
        # Render text (giữ nguyên như bạn đã có)
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
            text_x = self.collision_rect.x + (self.collision_rect.width - text_surface.get_width()) // 2
            screen.blit(text_surface, (text_x, y_offset))
            y_offset += line_height + 5
