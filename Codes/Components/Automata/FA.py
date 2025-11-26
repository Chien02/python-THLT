import math
import pygame
import random
from enum import Enum
from tweener import *
from Codes.Utils.FrameLoader import FrameLoader
from Codes.Components.Automata.RandomFAGenerate import RandomAutomatonGenerator
from Codes.Components.Automata.AutomatonLayoutMixin import AutomatonLayoutMixin

class SPRITE_TYPE(Enum):
    NORMAL = 0
    RIGHT =  1
    WRONG = 2

class FA:
    TYPE = ["start_state", "state", "end_state"]
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    BLACK = (0, 0, 0)

    def __init__(self, pattern_string, screen_size):
        self.pattern = pattern_string.lower()
        self.screen_size = screen_size

        # Sẽ được tạo từ RandomAutomatonGenerator
        self.states = []
        self.transitions = {}       # {from: {char: [to...]}}
        self.start_state = None
        self.accept_states = set()
        self.alphabet = set(pattern_string)

        self.state_positions = {}
        self.state_states = {}
        self.current_state = None

        self.automaton_generator = RandomAutomatonGenerator()
        self.layour_mixin = AutomatonLayoutMixin()

        # Danh sách các rect của state, dùng để kiểm tra input là click chuột
        # Các rect này sẽ được khởi tạo sau khi đã tính toán xong vị trí của các state
        # Kích thước của các rect là như nhau, và kích thước phụ thuộc vào kích thước sprite
        self.rect_size = (90, 90)
        self.state_rects = {} # {'q1': rect()}

        # Sprites
        self.looped_arrow = pygame.image.load("Assets/Images/Elements/Diagram/loop_arrow.png").convert_alpha()

        # Animation cho từng state (sẽ được init sau khi states được tạo)
        self.state_animations = {}  # {state_index: {'scale': Tween, 'shake': Tween}}
        
        # Animation cho toàn bộ diagram (khi hoàn thành)
        self.diagram_y_offset = 0  # Dịch chuyển lên
        self.diagram_alpha = 255    # Độ mờ
        self.diagram_move_tween = None
        self.diagram_fade_tween = None
        self.diagram_animating = False

        # Output được dùng để so sánh với chuỗi input
        self.output = ''
    
    
    def init(self, screen_width, screen_height):
        """
        Gọi random generator để tạo automaton phù hợp pattern_string.
        Layout cũng lấy từ random generator.
        """
        auto = self.automaton_generator.generate(self.pattern)
        self.states = auto["states"]
        self.start_state = auto["start"]
        self.accept_states = set(auto["accepts"])
        self.transitions = auto["transitions"]

        # Set sprite state
        for state in self.states:
            self.state_states[state] = {"current_sprite": SPRITE_TYPE.NORMAL.value}

        # Layout positions
        self.layour_mixin._generate_state_positions(self)
        print(f"From FA: {self.state_positions}")

        # Khởi tạo các rect cho
        self._init_state_rects()

        # Khởi tạo hình ảnh và animation cho các state
        self._init_state_animations()

        self.reset() # Về vị trí bắt đầu
        return True
    
    def _init_state_rects(self):
        """Khởi tạo rect cho từng state với vị trí tương ứng"""
        for state in self.states:
            pos = self.state_positions[state]
            self.state_rects[state] = pygame.Rect(pos[0], pos[1], self.rect_size[0], self.rect_size[1])
            self.state_rects[state].center = pos
    
    def reset(self):
        """Reset về start state"""
        self.current_state = self.start_state
        self.output = ''

    def is_next_state(self, state):
        for char in self.alphabet:
            to_list = self.transitions[self.current_state][char]
            if state in to_list:
                return char
        return None

    def update_current_state(self, char, new_state):
        """Cập nhật trạng thái của state hiện tại, đặt state hiện tại thành state mới và thêm kí tự mới vào output"""
        self.state_states[self.current_state]['current_sprite'] = SPRITE_TYPE.RIGHT.value
        self.output += char # Thêm kí tự được chọn vào output
        self.current_state = new_state

    def is_accepted(self):
        """Kiểm tra xem state hiện tại có phải accept state không"""
        return self.current_state in self.accept_states
    
    def check_pattern(self, output):
        n = len(output)
        for i in range(n):
            if output[i] != self.pattern[i]:
                return False
        return True
    
    def is_completed(self):
        """Kiểm tra xem 2 chuỗi input và output bằng nhau chưa"""
        return self.output == self.pattern

    #region Animation
    def _init_state_animations(self):
        """Khởi tạo animation cho mỗi state"""
        for state in self.states:
            self.state_animations[state] = {
                'scale': 1.0,          # Scale hiện tại
                'shake_x': 0.0,        # Offset X khi shake
                'tween_scale': None,   # Tween cho scale
                'tween_shake': None    # Tween cho shake
            }
    
    def _animate_state_correct(self, state_name):
        """
        Animation khi nhập đúng: Phóng to → Thu nhỏ (0.2s)
        
        Args:
            state_name: Tên của state cần animate
        """
        if state_name not in self.state_animations:
            return
        
        # Tạo tween scale: 1.0 → 1.3 → 1.0 (boomerang)
        scale_tween = Tween(
            begin=1.0,
            end=1.3,
            duration=100.0,  # 0.1s mỗi chiều = 0.2s tổng
            easing=Easing.BACK,
            easing_mode=EasingMode.OUT,
            boomerang=True
        )
        scale_tween.start()
        
        self.state_animations[state_name]['tween_scale'] = scale_tween
    
    def _animate_state_wrong(self, state_name):
        """
        Animation khi nhập sai: Phóng to + Lắc ngang (0.2s)
        
        Args:
            state_name: Tên của state cần animate
        """
        if state_name not in self.state_animations:
            return
        
        # Tween scale: 1.0 → 1.2 → 1.0
        scale_tween = Tween(
            begin=1.0,
            end=1.2,
            duration=100.0,
            easing=Easing.ELASTIC,
            easing_mode=EasingMode.OUT,
            boomerang=True
        )
        scale_tween.start()
        
        # Tween shake: 0 → 10 → -10 → 0 (lắc ngang)
        shake_tween = Tween(
            begin=0.0,
            end=10.0,
            duration=100.0,  # 0.1s mỗi chiều
            easing=Easing.SINE,
            easing_mode=EasingMode.IN_OUT,
            boomerang=True,
            loop=True,
            reps=2  # Lắc 2 lần
        )
        shake_tween.start()
        
        self.state_animations[state_name]['tween_scale'] = scale_tween
        self.state_animations[state_name]['tween_shake'] = shake_tween
    
    def _animate_diagram_complete(self):
        """
        Animation khi hoàn thành: Di chuyển lên + Mờ dần
        """
        self.diagram_animating = True
        
        # Tween di chuyển lên: 0 → -100 pixels
        self.diagram_move_tween = Tween(
            begin=0.0,
            end=-100.0,
            duration=500.0,  # 0.5s
            easing=Easing.CUBIC,
            easing_mode=EasingMode.OUT
        )
        self.diagram_move_tween.start()
        
        # Tween fade out: 255 → 0
        self.diagram_fade_tween = Tween(
            begin=255.0,
            end=0.0,
            duration=500.0,  # 0.5s
            easing=Easing.LINEAR
        )
        self.diagram_fade_tween.start()
    
    def _update_state_animations(self):
        """Update tất cả animation của các state"""
        for state, anim in self.state_animations.items():
            # Update scale tween
            if anim['tween_scale'] is not None:
                anim['tween_scale'].update()
                anim['scale'] = anim['tween_scale'].value
                
                # Xóa tween khi hoàn thành
                if not anim['tween_scale'].animating:
                    anim['tween_scale'] = None
                    anim['scale'] = 1.0  # Reset về 1.0
            
            # Update shake tween
            if anim['tween_shake'] is not None:
                anim['tween_shake'].update()
                anim['shake_x'] = anim['tween_shake'].value
                
                # Xóa tween khi hoàn thành
                if not anim['tween_shake'].animating:
                    anim['tween_shake'] = None
                    anim['shake_x'] = 0.0  # Reset về 0
                    self.analyzer.stop_analyze() # đợi hết animation mới thoát ra ngoài
    
    def _update_diagram_animation(self):
        """Update animation của toàn bộ diagram"""
        if self.diagram_move_tween is not None:
            self.diagram_move_tween.update()
            self.diagram_y_offset = self.diagram_move_tween.value
            
            # Kiểm tra xem animation đã xong chưa
            if not self.diagram_move_tween.animating:
                self.diagram_move_tween = None
        
        if self.diagram_fade_tween is not None:
            self.diagram_fade_tween.update()
            self.diagram_alpha = self.diagram_fade_tween.value
            
            # Kiểm tra xem animation đã xong chưa
            if not self.diagram_fade_tween.animating:
                self.diagram_fade_tween = None
                
                #  Khi cả 2 animation đều xong, gọi stop_analyze
                if self.diagram_move_tween is None:
                    self.diagram_animating = False
                    self.analyzer.stop_analyze()
    #endregion

    #region Drawing
    def draw_diagram(self, screen, state_sprites):
        """
        Vẽ sơ đồ DFA lên screen
        Args:
            screen: Pygame surface
            state_sprites: List các sprite cho states [normal, accept, refuse]
        """
        #   Nếu đang animate diagram, tạo surface tạm với alpha
        if self.diagram_animating:
            # Tạo surface tạm với kích thước màn hình
            temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            temp_surface.set_alpha(int(self.diagram_alpha))
            
            # Vẽ lên surface tạm
            self._draw_transitions(temp_surface)
            self._draw_states(temp_surface, state_sprites)
            # self._draw_info(temp_surface)
            
            # Blit surface tạm lên screen với offset
            screen.blit(temp_surface, (0, self.diagram_y_offset))
        else:
            # Vẽ bình thường
            self._draw_transitions(screen)
            self._draw_states(screen, state_sprites)
            # self._draw_info(screen)

    def _draw_states(self, screen, state_sprites):
        """Vẽ các state với animation"""
        font = pygame.font.Font(None, 32)
        
        for state in self.states:
            # Lấy vị trí gốc
            base_pos = self.state_positions[state]
            
            # Áp dụng animation
            anim = self.state_animations[state]
            scale = anim['scale']
            shake_x = anim['shake_x']
            
            # Vị trí cuối cùng = vị trí gốc + shake
            pos = (base_pos[0] + shake_x, base_pos[1])
            
            # Chọn sprite phù hợp
            sprite_idx = self.state_states[state]["current_sprite"]
            sprite = state_sprites[sprite_idx]
            
            # Scale sprite nếu cần
            if scale != 1.0:
                original_size = sprite.get_size()
                new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                sprite = pygame.transform.scale(sprite, new_size)
            
            # Vẽ rect của sprite tương ứng ---> Debug
            pygame.draw.rect(screen, (255, 0, 0), self.state_rects[state], 1)
            
            # Vẽ sprite
            sprite_rect = sprite.get_rect(center=pos)
            screen.blit(sprite, sprite_rect)
            
            # Vẽ vòng tròn cho accept_states
            if state in self.accept_states:
                radius = int(50 * scale)  # Scale viền theo sprite
                pygame.draw.circle(screen, self.WHITE, pos, radius, 4)
            
            # Vẽ tên state
            text = font.render(state, True, self.WHITE)
            text_rect = text.get_rect(center=pos)
            screen.blit(text, text_rect)

    def _draw_transitions(self, screen):
        """Vẽ tất cả transition theo cấu trúc edges: mỗi from_state đi đến to_state với danh sách các nhãn"""
        font = pygame.font.Font(None, 38)

        # Vẽ mũi tên start → q0
        start_pos = self.state_positions[self.start_state]
        start_arrow_pos = (start_pos[0] - 100, start_pos[1])
        self._draw_arrow(screen, start_arrow_pos, start_pos, "", font, False, True)

        for from_state in self.states:
            edges = self.collect_chars_from_same_next_state(from_state)
            if not edges: continue
            # Duyệt qua từng to_state, vẽ mũi tên đi đến từng next_state đó
            # với mũi tên sẽ được truyền vào danh sách các nhãn từ from_state đến to_state
            for to_state in edges:
                if from_state == to_state:
                    self._draw_self_loop(screen, to_state, edges[to_state], font)
                else:
                    from_pos = self.state_positions[from_state]
                    to_pos = self.state_positions[to_state]
                    self._draw_arrow(screen, from_pos, to_pos, edges[to_state], font)


    def collect_chars_from_same_next_state(self, from_state):
        edges : dict = {}                  # Danh sách các nhãn dẫn đến cùng trạng thái tiếp theo - {'to_state': ['a', 'm']}
        to_states = []                      # Danh sách các trạng thái tiếp theo từ trạng thái hiện tại
        for char, to_list in self.transitions[from_state].items():
            # Khởi tạo dict lần đầu duyệt
            if len(to_states) == 0:
                to_states = to_list
                for state in to_states:
                    edges[state] = [char]
            else:
                for state in to_list:
                    # Nếu phát hiện có state đã xuất hiện thì thêm kí tự mới vào.
                    if state in edges:
                        edges[state].append(char)
        
        # kết quả trả về edges với danh sách các mũi tên cần vẽ đi từ A đến to_list
        return edges


    def _draw_arrow(self, screen, start, end, chars, font, adjust_start=True, adjust_end=True):
        """
        Vẽ mũi tên từ start đến end với danh sách các nhãn
        
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
        
        # Vẽ mũi tên
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
        
        # Vẽ các nhãn
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
            
        # Offset label để không đè lên mũi tên
        # Tính vector vuông góc
        perp_dx = -dy
        perp_dy = dx
        offset = 20
        label_x = mid_x + perp_dx * offset
        label_y = mid_y + perp_dy * offset

        # Nếu có nhiều hơn 1 char thì bổ sung thêm dấu phẩy ở giữa
        for idx, char in enumerate(chars):
            text_surf = font.render(char, True, (0, 0, 0))
            text_width = text_surf.get_width()
            label_offset_x = text_width + 10
            text_rect = text_surf.get_rect(center=(label_x + (idx * label_offset_x), label_y))
                
            bg_rect = text_rect.inflate(8, 6)
            bg_rect_color = self.WHITE
            bg_border_color = self.BLACK

            if start == self.state_positions[self.current_state]:
                bg_rect_color = self.YELLOW

            pygame.draw.rect(screen, bg_rect_color, bg_rect) # foreground
            pygame.draw.rect(screen, bg_border_color, bg_rect, 2) # border
            screen.blit(text_surf, text_rect)

            # Thêm ',' nếu ko phải lần lặp đầu
            if idx == 0: return
            comma_surf = font.render(',', True, (0, 0, 0))
            comma_rect = comma_surf.get_rect(center=(label_x + (idx * label_offset_x // 2), label_y))
            screen.blit(comma_surf, comma_rect)

    def _draw_self_loop(self, screen, state, chars: list, font):
        """Vẽ self-loop cho một state."""
        pos = self.state_positions[state]
        x, y = pos

        loop_radius = 40
        loop_offset = -70  # vẽ phía trên node

        # Tâm của vòng loop
        loop_center = (x, y + loop_offset)
       
        # Vẽ hình mũi tên tự trỏ vào chính nó
        arrow_rect = self.looped_arrow.get_rect(center=loop_center)
        screen.blit(self.looped_arrow, arrow_rect)

        # Vẽ label
        for idx, char in enumerate(chars):
            text = font.render(char, True, (0, 0, 0))
            text_width = text.get_width()
            offset_x = text_width + 15 
            text_rect = text.get_rect(center=(loop_center[0] + (idx * offset_x), loop_center[1] - loop_radius - 5)) # Nhãn sẽ dính một phần vào mũi tên để phân biệt

            bg_rect = text_rect.inflate(8, 6) # Background cho phần text
            bg_rect_color = self.WHITE
            if pos == self.state_positions[self.current_state]: # Cập nhật màu cho nhãn của state đang duyệt (current_state)
                bg_rect_color = self.YELLOW
            
            pygame.draw.rect(screen, bg_rect_color, bg_rect)
            pygame.draw.rect(screen, self.BLACK, bg_rect, 2)
            screen.blit(text, text_rect)

            # Thêm dấu phẩy nếu khác lần lặp đầu
            if idx == 0: return
            comma_surf = font.render(',', True, (0, 0, 0))
            comma_rect = comma_surf.get_rect(center=(loop_center[0] + (idx * offset_x), loop_center[1] - loop_radius - 5))
            screen.blit(comma_surf, comma_rect)

    #endregion
