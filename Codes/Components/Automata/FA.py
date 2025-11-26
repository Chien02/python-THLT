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
    CURRENT = 3

class FA:
    TYPE = ["start_state", "state", "end_state"]
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    BLACK = (0, 0, 0)

    def __init__(self, analyzer, pattern_string, screen_size):
        self.pattern = pattern_string.lower()
        self.screen_size = screen_size

        self.automaton_generator = RandomAutomatonGenerator() # Hàm tạo FA
        self.layour_mixin = AutomatonLayoutMixin() # Hàm sắp xếp vị trí cho các trạng thái

        auto = self.automaton_generator.generate(self.pattern)
        self.alphabet = set(pattern_string)
        self.states = auto["states"]
        self.start_state = auto["start"]
        self.accept_states = set(auto["accepts"])
        self.transitions = auto["transitions"]

        # Sắp xếp vị trí của các state
        self.state_positions = {}
        self.layour_mixin._generate_state_positions(self)
        print(f"From FA: {self.state_positions}")

        self.output = ''
        self.current_state = self.start_state # Trạng thái đang duyệt
        self.state_states = {} # Thể hiện trạng thái: Hiện tại - đúng - sai
        # Cài đặt trạng thái khởi đầu cho các state
        for state in self.states:
            if state == self.current_state:
                self.state_states[state] = {"current_sprite": SPRITE_TYPE.RIGHT.value}
            else:
                self.state_states[state] = {"current_sprite": SPRITE_TYPE.NORMAL.value}
        self.update_next_states()

        # Danh sách các rect của state, dùng để kiểm tra input là click chuột
        # Các rect này sẽ được khởi tạo sau khi đã tính toán xong vị trí của các state
        # Kích thước của các rect là như nhau, và kích thước phụ thuộc vào kích thước sprite
        self.rect_size = (110, 110)
        self.state_collision_rects = {} # {'q1': rect()}
        # Khởi tạo các collsion rect cho các state
        self._init_state_collision_rects()

        # Sprites
        self.looped_arrow = pygame.image.load("Assets/Images/Elements/Diagram/loop_arrow.png").convert_alpha()

        # Animation cho từng state (sẽ được init sau khi states được tạo)
        self.state_animations = {}  # {state_index: {'scale': Tween, 'shake': Tween}}
        # Khởi tạo hình ảnh và animation cho các state
        self._init_state_animations()
        
        # Animation cho toàn bộ diagram (khi hoàn thành)
        self.diagram_y_offset = 0  # Dịch chuyển lên
        self.diagram_alpha = 255    # Độ mờ
        self.diagram_move_tween = None
        self.diagram_fade_tween = None
        self.diagram_animating = False

        from Codes.Scenes.StringAnalyzerScene import StringAnalyzerScene
        self.analyzer : StringAnalyzerScene = analyzer # Quản lý quá trình xử lý chuỗi
        self.analyzing_flag = True
    
    def _init_state_collision_rects(self):
        """Khởi tạo rect cho từng state với vị trí tương ứng"""
        for state in self.states:
            pos = self.state_positions[state]
            rect = pygame.Rect(0, 0, self.rect_size[0], self.rect_size[1])
            rect.center = pos
            self.state_collision_rects[state] = rect

    #region Update
    def update(self, dt):
        # Update animations cho từng state
        self._update_state_animations()
        
        # Update diagram animation
        if self.diagram_animating:
            self._update_diagram_animation()
        
        # Dừng phân tích
        if not self.analyzing_flag: return

        # Kiểm tra để dừng

        if self.is_accepted() and self.is_completed():
            print("Analyzed!")
            self.analyzing_flag = False 
                
            # Trigger animation hoàn thành
            self._animate_diagram_complete()
            
            # Cộng điểm
            self.analyzer.main_scene.score.add_correct()
            return
            
        # Nếu như có kí tự bị gõ sai thì dừng.
        for state in self.states:
            if self.state_states[state]["current_sprite"] == SPRITE_TYPE.WRONG.value:
                self.analyzing_flag = False
                #   Trigger animation sai, delay việc stop_analyze để animation chạy xong
                self._animate_state_wrong(self.current_state)
                self.analyzer.main_scene.score.add_wrong()
                return

    def is_accepted(self):
        """Kiểm tra xem state hiện tại có phải accept state không"""
        return self.current_state in self.accept_states
    
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
    #endregion

    #region Event Handler
    def handle_events(self, events):
        """
        Xử lý click chuột vào state
        """
        for event in events:
            # Xử lý click chuột
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
            
            # FIX: Tìm state đầu tiên được click (không loop qua tất cả)
            clicked_state = None
            for state in self.state_collision_rects:
                if self.state_collision_rects[state].collidepoint(event.pos):
                    clicked_state = state
                    print(f"From FA: clicked at {state}")
                    break  # Dừng ngay sau khi tìm được state
            
            # Nếu không click vào state nào, bỏ qua
            if clicked_state is None:
                continue
            
            # Kiểm tra xem có transition từ current_state đến clicked_state không
            char = self._is_next_state(clicked_state)
            
            if char:
                # Chỉ return True nếu thực sự cập nhật được state
                self.update_current_state(char, clicked_state)
                return True
            else:
                # Nếu không có transition hợp lệ, cũng trả về True (consumed event)
                # hoặc False nếu muốn pass sự kiện xuống
                return False
        
        return False  # Không có sự kiện nào được xử lý
    
    def _is_next_state(self, state):
        """Kiểm tra state này có thuộc danh sách state kế tiếp của current_state không"""
        for char, to_list in self.transitions.get(self.current_state, {}).items():
            if state in to_list:
                print(f"From FA: {state} đã được chọn thuộc to_list, với char = {char}")
                return char
        return None

    def update_current_state(self, char, new_state):
        """Cập nhật trạng thái của state hiện tại, đặt state hiện tại thành state mới và thêm kí tự mới vào output"""
        self.state_states[self.current_state]['current_sprite'] = SPRITE_TYPE.RIGHT.value
        self.output += char # Thêm kí tự được chọn vào output
        self.current_state = new_state
        print(f"From FA: current_output = {self.output} - current_state = {self.current_state}")
        # Kiểm tra với mẫu đầu vào
        if not self.check_pattern():
            self.state_states[self.current_state]['current_sprite'] = SPRITE_TYPE.WRONG.value
        else:
            self.state_states[self.current_state]['current_sprite'] = SPRITE_TYPE.RIGHT.value
            self.update_next_states()
    
    def update_next_states(self):
        for to_list in self.transitions.get(self.current_state, {}).values():
            for state in to_list:
                self.state_states[state]['current_sprite'] = SPRITE_TYPE.CURRENT.value
    
    def check_pattern(self):
        """Kiểm tra xem có output có trùng với mẫu không"""
        n = len(self.output)
        for i in range(n):
            if self.output[i] != self.pattern[i]:
                return False
        return True
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
            self._draw_states(temp_surface, state_sprites)
            self._draw_transitions(temp_surface)
            # self._draw_info(temp_surface)
            
            # Blit surface tạm lên screen với offset
            screen.blit(temp_surface, (0, self.diagram_y_offset))
        else:
            # Vẽ bình thường
            self._draw_states(screen, state_sprites)
            self._draw_transitions(screen)
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
            pygame.draw.rect(screen, (255, 0, 0), self.state_collision_rects[state], 1)
            
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

                    # Kiểm tra khoảng cách - nếu cách nhau > 1 level thì dùng curved arrow
                    from_layer = self._get_state_layer(from_state)
                    to_layer = self._get_state_layer(to_state)
                    distance = abs(to_layer - from_layer)
                
                if distance > 1:
                    # Mũi tên cong cho khoảng cách xa
                    adjust_to_pos = (to_pos[0], to_pos[1]+45)
                    self._draw_curved_arrow(screen, from_pos, adjust_to_pos, edges[to_state], font)
                else:
                    # Mũi tên thẳng cho khoảng cách gần
                    self._draw_arrow(screen, from_pos, to_pos, edges[to_state], font)

    def _get_state_layer(self, state):
        """Lấy layer của state dựa trên BFS từ start_state"""
        from collections import deque
        
        visited = {self.start_state: 0}
        queue = deque([self.start_state])
        
        while queue:
            current = queue.popleft()
            if current == state:
                return visited[current]
            
            for next_states in self.transitions.get(current, {}).values():
                for next_state in next_states:
                    if next_state not in visited:
                        visited[next_state] = visited[current] + 1
                        queue.append(next_state)
        
        return 0

    def collect_chars_from_same_next_state(self, from_state):
        edges : dict = {}                  # Danh sách các nhãn dẫn đến cùng trạng thái tiếp theo - {'to_state': ['a', 'm']}
        for char, to_list in self.transitions[from_state].items():
            for state in to_list:
                # Khởi tạo danh sách nếu chưa có state này
                if state not in edges:
                    edges[state] = []
                # Thêm ký tự vào danh sách
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
        start_adj = (start[0] + dx * 55, start[1] + dy * 55) if adjust_start else start
        end_adj = (end[0] - dx * 55, end[1] - dy * 55) if adjust_end else end
        
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

            # Thêm ',' giữa các ký tự (không phải lần lặp cuối)
            if idx < len(chars) - 1:
                comma_surf = font.render(',', True, (0, 0, 0))
                comma_x = label_x + ((idx + 1) * label_offset_x) - label_offset_x // 2
                comma_rect = comma_surf.get_rect(center=(comma_x, label_y))
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
    
    def _draw_curved_arrow(self, screen, start, end, chars, font, adjust_start=True, adjust_end=True):
        """
        Vẽ mũi tên cong (quadratic Bézier curve) từ start đến end
        Dùng cho transition cách nhau > 1 level
        """
        import math
        
        # Tính toán hướng
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return
        
        dx /= distance
        dy /= distance
        
        # Điều chỉnh điểm bắt đầu và kết thúc
        start_adj = (start[0] + dx * 55, start[1] + dy * 55) if adjust_start else start
        end_adj = (end[0] - dx * 55, end[1] - dy * 55) if adjust_end else end
        
        # Tính control point cho Bézier curve
        # Control point nằm giữa start và end nhưng lệch sang phía phải
        mid_x = (start_adj[0] + end_adj[0]) // 2
        mid_y = (start_adj[1] + end_adj[1]) // 2
        
        # Vector vuông góc để lệch ra
        perp_dx = -dy
        perp_dy = dx
        curve_offset = distance * 0.5  # Độ cong = 40% khoảng cách
        
        control_x = mid_x + perp_dx * curve_offset # Quay xuống (đổi lại thành cộng -> quay lên)
        control_y = mid_y - perp_dy * curve_offset
        
        # Vẽ quadratic Bézier curve
        points = self._get_bezier_points(start_adj, (control_x, control_y), end_adj, 40)
        
        # Vẽ từng segment thay vì dùng draw.lines
        try:
            # Convert từng point thành tuple int
            points_tuple = []
            for p in points:
                pt = (int(round(p[0])), int(round(p[1])))
                points_tuple.append(pt)
            
            # Thay vì dùng pygame.draw.lines, vẽ từng đoạn thẳng nối các điểm
            if len(points_tuple) > 1:
                for i in range(len(points_tuple) - 1):
                    p1 = points_tuple[i]
                    p2 = points_tuple[i + 1]
                    pygame.draw.line(screen, (255, 255, 255), p1, p2, 3)
        except Exception as e:
            print(f"Error vẽ curved arrow: {e}")
            import traceback
            traceback.print_exc()
        
        # Vẽ mũi tên ở cuối đường cong
        # Tính hướng tại điểm cuối
        p1 = points[-2] if len(points) >= 2 else start_adj
        p2 = points[-1]
        angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        
        arrow_size = 15
        arrow_p1 = (
            p2[0] - arrow_size * math.cos(angle - math.pi/6),
            p2[1] - arrow_size * math.sin(angle - math.pi/6)
        )
        arrow_p2 = (
            p2[0] - arrow_size * math.cos(angle + math.pi/6),
            p2[1] - arrow_size * math.sin(angle + math.pi/6)
        )
        
        pygame.draw.polygon(screen, self.WHITE, [p2, arrow_p1, arrow_p2])
        
        # Vẽ các nhãn tại giữa đường cong
        mid_point = self._get_bezier_point(start_adj, (control_x, control_y), end_adj, 0.5)
        
        # Offset label để không đè lên mũi tên
        perp_dx_mid = -dy
        perp_dy_mid = dx
        offset = 25
        label_x = mid_point[0] + perp_dx_mid * offset
        label_y = mid_point[1] + perp_dy_mid * offset
        
        # Vẽ các ký tự
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

            pygame.draw.rect(screen, bg_rect_color, bg_rect)
            pygame.draw.rect(screen, bg_border_color, bg_rect, 2)
            screen.blit(text_surf, text_rect)

            # Thêm ',' giữa các ký tự
            if idx < len(chars) - 1:
                comma_surf = font.render(',', True, (0, 0, 0))
                comma_x = label_x + ((idx + 1) * label_offset_x) - label_offset_x // 2
                comma_rect = comma_surf.get_rect(center=(comma_x, label_y))
                screen.blit(comma_surf, comma_rect)

    def _get_bezier_point(self, p0, control, p2, t):
        """Tính điểm trên quadratic Bézier curve tại tham số t (0 <= t <= 1)"""
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * control[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * control[1] + t**2 * p2[1]
        return (x, y)

    def _get_bezier_points(self, p0, control, p2, num_points):
        """Tính danh sách điểm trên quadratic Bézier curve"""
        points = []
        for i in range(num_points + 1):
            t = i / num_points
            points.append(self._get_bezier_point(p0, control, p2, t))
        return points
    #endregion