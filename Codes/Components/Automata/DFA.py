import pygame
import math
from Codes.Components.Automata.FA import FA, SPRITE_TYPE
from Codes.Utils.TweenAnimation import Tween, Easing, EasingMode

class DFA(FA):
    def __init__(self, analyzer, pattern_string):
        """
        Khởi tạo DFA từ chuỗi pattern (linear matching)
        
        Args:
            pattern_string: Chuỗi cần khớp (ví dụ: "madam", "moon")
        """
        super().__init__(pattern_string)
        self.analyzer = analyzer
        self.analyzing_flag = True
        
        #   Animation cho từng state (sẽ được init sau khi states được tạo)
        self.state_animations = {}  # {state_index: {'scale': Tween, 'shake': Tween}}
        
        #   Animation cho toàn bộ diagram (khi hoàn thành)
        self.diagram_y_offset = 0  # Dịch chuyển lên
        self.diagram_alpha = 255    # Độ mờ
        self.diagram_move_tween = None
        self.diagram_fade_tween = None
        self.diagram_animating = False
    
    def _init_state_animations(self):
        """Khởi tạo animation cho mỗi state"""
        for state in self.states:
            self.state_animations[state] = {
                'scale': 1.0,          # Scale hiện tại
                'shake_x': 0.0,        # Offset X khi shake
                'tween_scale': None,   # Tween cho scale
                'tween_shake': None    # Tween cho shake
            }
    
    def _calculate_positions(self):
        super()._calculate_positions()
        #   Init animations SAU KHI states đã được tạo
        self._init_state_animations()
    
    def _animate_state_correct(self, state_index):
        """
        Animation khi nhập đúng: Phóng to → Thu nhỏ (0.2s)
        
        Args:
            state_index: Index của state cần animate
        """
        if state_index not in self.state_animations:
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
        
        self.state_animations[state_index]['tween_scale'] = scale_tween
    
    def _animate_state_wrong(self, state_index):
        """
        Animation khi nhập sai: Phóng to + Lắc ngang (0.2s)
        
        Args:
            state_index: Index của state cần animate
        """
        if state_index not in self.state_animations:
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
        
        self.state_animations[state_index]['tween_scale'] = scale_tween
        self.state_animations[state_index]['tween_shake'] = shake_tween
    
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
            #   Lấy vị trí gốc
            base_pos = self.state_positions[state]
            
            #   Áp dụng animation
            anim = self.state_animations[state]
            scale = anim['scale']
            shake_x = anim['shake_x']
            
            # Vị trí cuối cùng = vị trí gốc + shake
            pos = (base_pos[0] + shake_x, base_pos[1])
            
            # Chọn sprite phù hợp
            sprite_idx = self.state_states[state]["current_sprite"]
            sprite = state_sprites[sprite_idx]
            
            #   Scale sprite nếu cần
            if scale != 1.0:
                original_size = sprite.get_size()
                new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                sprite = pygame.transform.scale(sprite, new_size)
            
            # Vẽ sprite
            sprite_rect = sprite.get_rect(center=pos)
            screen.blit(sprite, sprite_rect)
            
            # Highlight state hiện tại với viền vàng
            if state == self.current_state:
                radius = int(50 * scale)  # Scale viền theo sprite
                pygame.draw.circle(screen, self.YELLOW, pos, radius, 4)
            
            # Vẽ tên state
            text = font.render(str(state), True, self.WHITE)
            text_rect = text.get_rect(center=pos)
            screen.blit(text, text_rect)
    
    def handle_events(self, events):
        """
        Xử lý từng kí tự nhập vào và trả về kết quả
        
        Returns:
            tuple: (accepted: bool, path: list of states)
        """
        if self.analyzing_flag == False:
            return False
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.unicode:  # Nhận tất cả
                    char = event.unicode
                    if char == str(self.transitions[self.current_index][1]): # current_state's label to next_state
                        self.state_states[self.current_index]["current_sprite"] = SPRITE_TYPE.RIGHT.value
                        
                        # Trigger animation đúng
                        self._animate_state_correct(self.current_index)
                        self.get_next_state()
                        # print(f"{self.get_next_state()} - accept state: {self.accept_state}")
                    else:
                        self.state_states[self.current_index]["current_sprite"] = SPRITE_TYPE.WRONG.value
                        
                return True
        return False
    
    def update(self, dt):
        #   Update animations cho từng state
        self._update_state_animations()
        
        #   Update diagram animation
        if self.diagram_animating:
            self._update_diagram_animation()
        
        if not self.analyzing_flag: 
            return
            
        # Nếu như có kí tự bị gõ sai thì dừng.
        for state in self.states:
            if state == self.accept_state and self.state_states[state]["current_sprite"] == SPRITE_TYPE.RIGHT.value:
                print("Analyzed!")
                self.analyzing_flag = False
                
                #   Trigger animation hoàn thành
                self._animate_diagram_complete()
                
                # Delay việc stop_analyze để animation chạy xong
                return
                
            if self.state_states[state]["current_sprite"] == SPRITE_TYPE.WRONG.value:
                self.analyzing_flag = False
                #   Trigger animation sai, delay việc stop_analyze để animation chạy xong
                self._animate_state_wrong(self.current_index)
                return
    
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