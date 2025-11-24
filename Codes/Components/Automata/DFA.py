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
        from Codes.Scenes.StringAnalyzerScene import StringAnalyzerScene
        self.analyzer : StringAnalyzerScene = analyzer
        self.analyzing_flag = True
    
    def handle_events(self, events):
        """
        Xử lý input chuột
        """
        if self.analyzing_flag == False:
            return False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # ĐIỀU KIỆN KIỂM TRA:
                # - State được chọn thuộc next_state của current_state
                # - Kí tự được thêm vào phải đảm bảo đúng pattern
                # Nếu click chuột vào state thì kiểm tra xem state đó có phải là state tiếp theo có thể đi từ state hiện tại không
                # Đúng thì thêm chuyển trạng thái của state hiện tại thành đúng và cập nhật state hiện tại thành state mới
                # Kiểm tra bằng cách nhận biết xem chuột có click vào rect của state hay không?
                for state in self.state_rects:
                    if self.state_rects[state].collidepoint(event.pos):
                        char = self.is_next_state(state) # nếu đúng thì trả về kí tự đi đến state được chọn, ngược lại trả về None
                        if not char: return # Chọn không đúng state next state thì không làm gì cả - trường hợp người chơi bấm thẳng vào accept state

                        temp_output = self.output + char
                        if not self.check_pattern(temp_output): # Chọn đúng next_state nhưng không tạo đúng chuỗi
                            # Trừ điểm
                            self.state_states[self.current_state]["current_sprite"] = SPRITE_TYPE.WRONG.value
                            self.analyzer.main_scene.score.add_wrong()
                        else:
                            self.update_current_state(char, state)
                        return True
        return False
    
    def update(self, dt):
        #   Update animations cho từng state
        self._update_state_animations()
        
        #   Update diagram animation
        if self.diagram_animating:
            self._update_diagram_animation()
        
        if not self.analyzing_flag: return

        # Kiểm tra để dừng
        if self.is_accepted() and self.is_completed():
            print("Analyzed!")
            self.analyzing_flag = False 
                
            #   Trigger animation hoàn thành
            self._animate_diagram_complete()
                
            # Delay việc stop_analyze để animation chạy xong
            return
            
        # Nếu như có kí tự bị gõ sai thì dừng.
        for state in self.states:
            if self.state_states[state]["current_sprite"] == SPRITE_TYPE.WRONG.value:
                self.analyzing_flag = False
                #   Trigger animation sai, delay việc stop_analyze để animation chạy xong
                self._animate_state_wrong(self.current_state)
                return
    
    