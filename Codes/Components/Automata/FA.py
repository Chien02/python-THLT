import math
import pygame
from enum import Enum

class SPRITE_TYPE(Enum):
    NORMAL = 0
    RIGHT =  1
    WRONG = 2

class FA:
    TYPE = ["start_state", "state", "end_state"]
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    BLACK = (0, 0, 0)

    def __init__(self, pattern_string):
        self.pattern = pattern_string.lower()
    
        self.states = []
        self.alphabet = set(pattern_string)
        self.transitions = [] # List of (from state, char, to state)
        self.start_state = ''
        self.accept_state = ''
        self.accepted = True

        # Visualization
        self.state_positions = {}
        self.state_states = {} # state 0: current_state = normal
        self.current_state = None
        self.current_state_idx = 0
    
    def init(self):
        """Xây dựng DFA từ pattern string"""
        self._build_states()
        self._build_transitions()
        self._calculate_positions()
        self.reset()
        return True
    
    def _build_states(self):
        """Tạo state tuyến tính đi từ đầu đến cuối"""
        n = len(self.pattern)

        # Tạo n+1 states: 0, 1, 2, 3
        self.states = [i for i in range(0, n+1)]
        self.start_state = 0
        self.accept_state = n

        # Theo dõi trạng thái của từng state đó
        for state in self.states:
            self.state_states[state] = {"current_sprite": SPRITE_TYPE.NORMAL.value}

    def _build_transitions(self):
        """Xây dựng transitions tuyến tính theo pattern"""
        n = len(self.pattern)

        # Xây dựng transitions chính theo pattern
        for i in range(0, n):
            from_state = i
            char = self.pattern[i]
            to_state = i + 1
            self.transitions.append((from_state, char, to_state))
    
    def _calculate_positions(self, screen_width=800, screen_height=600):
        """
        Tính toán vị trí các state để vẽ sơ đồ (căn giữa màn hình)
        
        Args:
            screen_width: Chiều rộng màn hình
            screen_height: Chiều cao màn hình
        """
        n = len(self.states)
        
        # Layout ngang: các state xếp thành một hàng ngang
        spacing = 150  # Khoảng cách giữa các state
        
        # Tính tổng chiều rộng của đồ thị
        total_width = (n - 1) * spacing
        
        # Căn giữa theo chiều ngang
        start_x = (screen_width - total_width) / 2
        
        # Căn giữa theo chiều dọc
        y = screen_height / 2
        
        for i, state in enumerate(self.states):
            x = start_x + i * spacing
            self.state_positions[state] = (x, y)
    
    def reset(self):
        """Reset về start state"""
        self.current_state = self.start_state
        self.current_index = 0

    def get_next_state(self):
        if self.current_state != self.accept_state:
            self.current_index += 1
            print(f"Current_index: {self.current_index}")
            self.current_state = self.states[self.current_index]

            if self.current_state == self.accept_state:
                print("Found accepted state")
                self.state_states[self.current_index]["current_sprite"] = SPRITE_TYPE.RIGHT.value
            return self.current_state
    
    def is_accepted(self):
        """Kiểm tra xem state hiện tại có phải accept state không"""
        return self.current_state == self.accept_state

    def get_transition_table(self):
        """Trả về bảng transitions dạng dict để debug"""
        return {
            'states': self.states,
            'alphabet': list(self.alphabet),
            'transitions': self.transitions,
            'start_state': self.start_state,
            'accept_state': self.accept_state
        }

    def print_info(self):
        """In thông tin DFA ra console (để debug)"""
        print(f"\n=== DFA for pattern: '{self.pattern}' ===")
        print(f"States: {', '.join(self.states)}")
        print(f"Alphabet: {{{', '.join(sorted(self.alphabet))}}}")
        print(f"Start state: {self.start_state}")
        print(f"Accept state: {self.accept_state}")
        print("\nTransitions:")
        for from_s, char, to_s in self.transitions:
            print(f"  {from_s} --{char}--> {to_s}")
        print("=" * 40)

    def _draw_info(self, screen):
        """Vẽ thông tin về DFA"""
        font_large = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 28)
        
        # Pattern với highlight
        pattern_text = f"Pattern: "
        text = font_large.render(pattern_text, True, (0, 0, 0))
        screen.blit(text, (20, 20))
        
        # Vẽ pattern với highlight cho phần đã match
        x_offset = 20 + text.get_width()
        for i, char in enumerate(self.pattern):
            if i < self.current_index:
                color = (0, 150, 0)  # Xanh lá cho phần đã match
            elif i == self.current_index:
                color = (255, 150, 0)  # Cam cho ký tự tiếp theo
            else:
                color = (100, 100, 100)  # Xám cho phần chưa match
            
            char_text = font_large.render(char, True, color)
            screen.blit(char_text, (x_offset, 20))
            x_offset += char_text.get_width() + 5
        
        # Current state
        state_text = f"Current State: {self.current_state}"
        color = (0, 150, 0) if self.is_accepted() else (0, 0, 0)
        text = font_small.render(state_text, True, color)
        screen.blit(text, (20, 65))
        
        # Progress
        progress_text = f"Progress: {self.current_index}/{len(self.pattern)}"
        text = font_small.render(progress_text, True, (0, 0, 0))
        screen.blit(text, (20, 95))
        
        # Status
        if self.is_accepted():
            status_text = "ACCEPTED - Pattern matched!"
            text = font_large.render(status_text, True, (0, 150, 0))
            screen.blit(text, (20, 130))
        elif self.current_index > 0:
            status_text = f"Matching... ({self.current_index}/{len(self.pattern)})"
            text = font_small.render(status_text, True, (255, 150, 0))
            screen.blit(text, (20, 130))
        
    # Drawing section
    def _draw_states(self, screen, state_sprites):
        """Vẽ các state"""
        font = pygame.font.Font(None, 32)
        
        for state in self.states:
            pos = self.state_positions[state]
            
            # Chọn sprite phù hợp
            sprite_idx = self.state_states[state]["current_sprite"]
            
            # Vẽ sprite
            sprite = state_sprites[sprite_idx]
            sprite_rect = sprite.get_rect(center=pos)
            screen.blit(sprite, sprite_rect)
            
            # Highlight state hiện tại với viền vàng
            if state == self.current_state:
                pygame.draw.circle(screen, self.YELLOW, pos, 50, 4)
            
            # Vẽ tên state
            text = font.render(str(state), True, self.WHITE)
            text_rect = text.get_rect(center=pos)
            screen.blit(text, text_rect)
    
    def _draw_transitions(self, screen):
        """Vẽ các transitions"""
        font = pygame.font.Font(None, 28)
        
        # Vẽ mũi tên trỏ vào trạng thái bắt đầu
        start_arrow_pos = (10, 300)
        self._draw_arrow(screen, start_arrow_pos, self.state_positions[0], "", font, False, True)
        for from_state, char, to_state in self.transitions:
            from_pos = self.state_positions[from_state]
            to_pos = self.state_positions[to_state]
            
            # Vẽ mũi tên
            self._draw_arrow(screen, from_pos, to_pos, char, font)
        
    def _draw_arrow(self, screen, start, end, label, font, adjust_start=True, adjust_end=True):
        """
        Vẽ mũi tên từ start đến end
        
        Args:
            adjust_start: Có rút ngắn điểm bắt đầu không (False cho start arrow)
            adjust_end: Có rút ngắn điểm kết thúc không
        """
        # Tính toán hướng
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return
        
        dx /= distance
        dy /= distance
        
        # Điều chỉnh có điều kiện
        if adjust_start:
            start_adj = (start[0] + dx * 55, start[1] + dy * 55)
        else:
            start_adj = start
            
        if adjust_end:
            end_adj = (end[0] - dx * 55, end[1] - dy * 55)
        else:
            end_adj = end
        
        # Vẽ đường thẳng
        line_color = self.WHITE
        pygame.draw.line(screen, line_color, start_adj, end_adj, 3)
        
        # Vẽ mũi tên (phần này giữ nguyên)
        arrow_size = 15
        angle = math.atan2(dy, dx)
        
        arrow_p1 = (
            end_adj[0] - arrow_size * math.cos(angle - math.pi/6),
            end_adj[1] - arrow_size * math.sin(angle - math.pi/6)
        )
        arrow_p2 = (
            end_adj[0] - arrow_size * math.cos(angle + math.pi/6),
            end_adj[1] - arrow_size * math.sin(angle + math.pi/6)
        )
        
        pygame.draw.polygon(screen, line_color, [end_adj, arrow_p1, arrow_p2])
        
        # Vẽ label (giữ nguyên phần này)
        if label != "":
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2 - 20
            
            text = font.render(label, True, (0, 0, 0))
            text_rect = text.get_rect(center=(mid_x, mid_y))
            
            bg_rect = text_rect.inflate(8, 6)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect, 2)
            screen.blit(text, text_rect)