import pygame
import json
import os
import random

from Codes.Utils.FrameLoader import FrameLoader
from Codes.Utils.SpriteFrame import SpriteFrames

class Score:
    """
    Class quản lý điểm số cho game
    - Cộng điểm khi nhập đúng
    - Trừ điểm khi nhập sai
    - Lưu high score
    - Hiển thị điểm và combo
    """
    YELLOW = (255, 215, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 100, 100)
    MIXED_RED = (174, 35, 52)
    BRIGHT_YELLOW = (251, 255, 134)

    def __init__(self, 
                 correct_points=10, 
                 wrong_points=-5,
                 combo_multiplier=1.5,
                 save_file="Data/highscore.json"):
        """
        Khởi tạo Score Manager
        
        Args:
            correct_points: Điểm cộng khi đúng
            wrong_points: Điểm trừ khi sai (số âm)
            combo_multiplier: Hệ số nhân cho combo
            save_file: Đường dẫn file lưu high score
        """
        self.correct_points = correct_points
        self.wrong_points = wrong_points
        self.combo_multiplier = combo_multiplier
        self.save_file = save_file
        
        # Điểm hiện tại
        self.current_score = 0
        
        # Combo system
        self.combo = 0
        self.max_combo = 0
        
        # Thống kê
        self.total_correct = 0
        self.total_wrong = 0
        self.total_patterns = 0
        
        # High score
        self.high_score = self._load_high_score()
        
        # Animation effect
        self.score_popup = None  # (text, timer, color, type = correct or wrong)
        self.popup_duration = 1.0  # 1 giây
        self.POPUP_TYPE = ('correct', 'wrong')

        #region Visual
        self.current_score_sprite = pygame.image.load("Assets/Images/UIs/Score/current_score.png").convert_alpha()
        self.high_score_sprite = pygame.image.load("Assets/Images/UIs/Score/high_score.png").convert_alpha()
        self.combo_state_1 = pygame.image.load("Assets/Images/UIs/Score/combo_state1.png").convert_alpha()
        self.combo_state_2 = pygame.image.load("Assets/Images/UIs/Score/combo.png").convert_alpha()

        self.combo1_sprite_x, self.combo1_sprite_y = (139, 51)
        self.combo2_sprite_x, self.combo2_sprite_y = (184, 92)
        self.combo_1_sprite = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Score/combo_state1.png", self.combo1_sprite_x, self.combo1_sprite_y, num_frames=1) 
        self.combo_2_sprite = FrameLoader.load_frames_from_sheet("Assets/Images/UIs/Score/combo2.png", self.combo2_sprite_x, self.combo2_sprite_y, num_frames=4)
        self.combo_sprite = SpriteFrames()
        self.combo_sprite.add_animation('state1', self.combo_1_sprite, frame_duration=1)
        self.combo_sprite.add_animation('state2', self.combo_2_sprite, frame_duration=0.2)
        self.combo_sprite.set_default_animation('state1')
        self.combo_sprite.play('state1')

        self.popup_correct_sprite = pygame.image.load("Assets/Images/UIs/Score/correct.png").convert_alpha()
        self.popup_wrong_sprite = pygame.image.load("Assets/Images/UIs/Score/wrong.png").convert_alpha()
        
        #endregion
        
    def add_correct(self, bonus_points=0):
        """
        Cộng điểm khi nhập đúng
        
        Args:
            bonus_points: Điểm thưởng thêm (ví dụ: dựa trên độ dài pattern)
            
        Returns:
            int: Số điểm được cộng
        """
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.total_correct += 1
        self.total_patterns += 1
        
        # Tính điểm với combo multiplier
        base_points = self.correct_points + bonus_points
        combo_bonus = 0
        
        if self.combo >= 5:
            # Combo từ 5 trở lên: nhân hệ số
            combo_bonus = int(base_points * (self.combo_multiplier - 1))
        
        total_points = base_points + combo_bonus
        self.current_score += total_points
        
        # Cập nhật high score - Sự kiện cập nhật highscore
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self._save_high_score()
        
        # Tạo popup hiển thị điểm
        if combo_bonus > 0:
            popup_texts = [f"{total_points}", f"x({self.combo})!"]
        else:
            popup_texts = [f"{total_points}"]
        
        random_x = random.randrange(-100, 100, 25)
        random_y = random.randrange(10, 60, 10)
        random_pos = (random_x, random_y)

        self.score_popup = (popup_texts, self.popup_duration, self.BRIGHT_YELLOW, random_pos, self.POPUP_TYPE[0])
        
        return total_points
    
    def add_wrong(self, attemp=1):
        """
        Trừ điểm khi nhập sai
        
        Returns:
            int: Số điểm bị trừ (số âm)
        """
        self.combo = 0  # Reset combo
        self.total_wrong += 1
        self.total_patterns += 1
        
        points = self.wrong_points * attemp
        self.current_score = max(0, self.current_score + points)  # Không cho điểm âm

        random_x = random.randrange(-100, 100, 25)
        random_y = random.randrange(10, 60, 10)
        random_pos = (random_x, random_y)
        # Tạo popup hiển thị điểm bị trừ
        self.score_popup = ([f"{points*(-1)}"], self.popup_duration, self.WHITE, random_pos, self.POPUP_TYPE[1])
        
        return points
    
    def get_accuracy(self):
        """
        Tính tỉ lệ chính xác
        
        Returns:
            float: Phần trăm chính xác (0-100)
        """
        if self.total_patterns == 0:
            return 0.0
        return (self.total_correct / self.total_patterns) * 100
    
    def reset(self):
        """Reset điểm về 0 (giữ nguyên high score)"""
        self.current_score = 0
        self.combo = 0
        self.total_correct = 0
        self.total_wrong = 0
        self.total_patterns = 0
        self.score_popup = None
    
    def reset_all(self):
        """Reset tất cả bao gồm high score"""
        self.reset()
        self.high_score = 0
        self.max_combo = 0
        self._save_high_score()
    
    def get_rank(self):
        """
        Lấy rank dựa trên điểm số
        
        Returns:
            str: Rank (S, A, B, C, D, F)
        """
        if self.current_score >= 1000:
            return "S"
        elif self.current_score >= 500:
            return "A"
        elif self.current_score >= 300:
            return "B"
        elif self.current_score >= 150:
            return "C"
        elif self.current_score >= 50:
            return "D"
        else:
            return "F"
    
    def _load_high_score(self):
        """Load high score từ file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except Exception as e:
            print(f"Error loading high score: {e}")
        return 0
    
    def _save_high_score(self):
        """Lưu high score vào file"""
        try:
            # Tạo thư mục nếu chưa có
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            
            with open(self.save_file, 'w') as f:
                data = {
                    'high_score': self.high_score,
                    'max_combo': self.max_combo
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving high score: {e}")
    
    def update(self, dt):
        """
        Cập nhật animations (popup) và animated combo (nếu có)
        
        Args:
            dt: Delta time
        """
        # Draw combo
        self.combo_sprite.update(dt)

        if self.score_popup:
            random_x = random.randrange(-100, 100, 25)
            random_y = random.randrange(10, 60, 10)
            random_pos = (random_x, random_y)
            texts, timer, color, random_pos, popup_type = self.score_popup
            timer -= dt
            if timer <= 0:
                self.score_popup = None
            else:
                self.score_popup = (texts, timer, color, random_pos, popup_type)

    def draw(self, surface: pygame.Surface, x=20, y=20):
        """
        Vẽ điểm số lên màn hình
        
        Args:
            surface: Pygame surface
            x, y: Vị trí góc trên bên trái
        """
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        # Điểm hiện tại
        padding = 20
        score_text = f"{self.current_score}"
        score_surf = font_large.render(score_text, True, self.WHITE)
        score_sprite_rect = self.current_score_sprite.get_rect(topleft = (x, y))
        score_text_rect = score_surf.get_rect()
        score_text_rect.midright = (score_sprite_rect.midright[0] - padding, score_sprite_rect.midright[1])
        
        surface.blit(self.current_score_sprite, score_sprite_rect)
        surface.blit(score_surf, score_text_rect)
        
        # High score
        high_score_pos = (x, y + 75) # Thấp hơn current_score
        high_score_sprite_rect = self.high_score_sprite.get_rect(topleft = high_score_pos)
        high_score_text = f"{self.high_score}"
        high_score_surf = font_small.render(high_score_text, True, self.YELLOW)
        high_score_text_rect = high_score_surf.get_rect()
        high_score_text_rect.midright = (high_score_sprite_rect.midright[0] - padding, high_score_sprite_rect.centery)
        best_text = "BEST:"
        best_text_surf = font_small.render(best_text, True, self.YELLOW)
        best_text_rect = best_text_surf.get_rect(midleft = (x + padding, 
                                                            high_score_sprite_rect.centery))

        surface.blit(self.high_score_sprite, high_score_sprite_rect)
        surface.blit(best_text_surf, best_text_rect)
        surface.blit(high_score_surf, high_score_text_rect)
        
        # Combo
        combo_state1_pos = (x, high_score_pos[1] + 60)
        combo_state2_pos = (10, high_score_pos[1] + 30)
        combo1_sprite_rect = self.combo_state_1.get_rect(topleft = combo_state1_pos)
        combo2_sprite_rect = self.combo_state_2.get_rect(topleft = combo_state2_pos)
        combo_sprite_rect = None

        if self.combo > 0:
            combo_text = f"Combo: x{self.combo}"
            combo_color = self.RED if self.combo >= 5 else self.WHITE
            combo_surf = font_medium.render(combo_text, True, combo_color)
            combo_rect = combo_surf.get_rect()
            
            if self.combo >= 5:
                # state2
                self.combo_sprite.play('state2', loop=True)
                combo_sprite_rect = combo2_sprite_rect
                combo_rect.center = (combo2_sprite_rect.midleft[0] + 80, combo2_sprite_rect.top + 52) # It's own padding
            else:
                # state1
                self.combo_sprite.play('state1', loop=True)
                combo_rect.center = combo1_sprite_rect.center
                combo_sprite_rect = combo1_sprite_rect

            # Draw animated frame
            current_frame = self.combo_sprite.get_current_frame()
            if not current_frame:
                current_frame = self.combo_state_1
            surface.blit(current_frame, combo_sprite_rect)
            surface.blit(combo_surf, combo_rect)
        
        # Accuracy
        # accuracy_text = f"Accuracy: {self.get_accuracy():.1f}%"
        # accuracy_surf = font_small.render(accuracy_text, True, (100, 200, 255))
        # surface.blit(accuracy_surf, (x + 5, y + 120))
        
        # Rank
        # rank = self.get_rank()
        # rank_colors = {
        #     'S': (255, 215, 0),   # Gold
        #     'A': (255, 100, 100), # Red
        #     'B': (100, 150, 255), # Blue
        #     'C': (100, 255, 150), # Green
        #     'D': (200, 200, 200), # Gray
        #     'F': (100, 100, 100)  # Dark gray
        # }
        # rank_text = f"Rank: {rank}"
        # rank_surf = font_medium.render(rank_text, True, rank_colors.get(rank, (255, 255, 255)))
        # surface.blit(rank_surf, (x, y + 145))
        
        # Score popup (animation khi cộng/trừ điểm)
        if self.score_popup:
            texts, timer, color, random_pos, popup_type = self.score_popup

            # Chọn sprite phù hợp với loại popup
            popup_sprite = None
            if popup_type == self.POPUP_TYPE[0]:
                popup_sprite = self.popup_correct_sprite
            else:
                popup_sprite = self.popup_wrong_sprite
            
            # Fade out effect
            alpha = int((timer / self.popup_duration) * 255)
            popup_surf = font_large.render(texts[0], True, color)
            popup_surf.set_alpha(alpha)
            # Vị trí di chuyển lên trên
            offset_y = int((1 - timer / self.popup_duration) * 50)
            
            popup_pos = ((surface.get_width() // 2) + random_pos[0], y + random_pos[1] + 100 - offset_y)
            # Nếu có combo thì bổ sung thêm text cho combo và vị trí (nằm ngoài sprite - dịch qua bên phải)
            combo_surf = None
            combo_rect = None
            if len(texts) > 1:
                combo_surf = font_large.render(texts[1], True, color)
                combo_rect = combo_surf.get_rect(center = (popup_pos[0] + 120, popup_pos[1]))
            
            popup_text_pos = (popup_pos[0] + 24, popup_pos[1] - 2)
            popup_rect = popup_surf.get_rect(center = popup_text_pos)
            popup_sprite_rect = popup_sprite.get_rect(center = popup_pos)
            
            if combo_rect and combo_surf:
                surface.blit(combo_surf, combo_rect)
            surface.blit(popup_sprite, popup_sprite_rect)
            surface.blit(popup_surf, popup_rect)
    
    def draw_only_score(self, screen, x, y):
        font_large = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 24)
        
        # Current
        padding = 20
        score_text = f"{self.current_score}"
        score_surf = font_large.render(score_text, True, self.WHITE)
        score_sprite_rect = self.current_score_sprite.get_rect(topleft = (x, y))
        score_text_rect = score_surf.get_rect()
        score_text_rect.midright = (score_sprite_rect.midright[0] - padding, score_sprite_rect.midright[1])
        
        screen.blit(self.current_score_sprite, score_sprite_rect)
        screen.blit(score_surf, score_text_rect)
        
        # High score
        high_score_pos = (x, y + 75) # Thấp hơn current_score
        high_score_sprite_rect = self.high_score_sprite.get_rect(topleft = high_score_pos)
        high_score_text = f"{self.high_score}"
        high_score_surf = font_small.render(high_score_text, True, self.YELLOW)
        high_score_text_rect = high_score_surf.get_rect()
        high_score_text_rect.midright = (high_score_sprite_rect.midright[0] - padding, high_score_sprite_rect.centery)
        best_text = "BEST:"
        best_text_surf = font_small.render(best_text, True, self.YELLOW)
        best_text_rect = best_text_surf.get_rect(midleft = (x + padding, 
                                                            high_score_sprite_rect.centery))

        screen.blit(self.high_score_sprite, high_score_sprite_rect)
        screen.blit(best_text_surf, best_text_rect)
        screen.blit(high_score_surf, high_score_text_rect)
        pass

    BRIGHT_GREY = (155, 171, 178)
    DARK = (46, 34, 47)
    def draw_summary(self, surface, screen_size, pos=(680, 390)):
        """
        Vẽ bảng tổng kết khi kết thúc game
        
        Args:
            surface: Pygame surface
            screen_width, screen_height: Kích thước màn hình
        """
        font_title = pygame.font.Font(None, 64)
        font_text = pygame.font.Font(None, 36)
        
        # Panel
        center = (screen_size[0] // 2, screen_size[1] // 2)
        panel_alpha = 220
        panel_width = 310
        panel_height = 240
        if pos:
            panel_x, panel_y = pos
        else:
            panel_x = (center[0] + panel_width) 
            panel_y = (center[1] - panel_height)
        
        r, g, b = self.DARK
        panel_color = (r, g, b, panel_alpha)

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_rect.center = (panel_x, panel_y)
        
        # pygame.draw.rect(surface, panel_color, panel_rect)
        pygame.draw.rect(surface, self.BRIGHT_GREY, panel_rect, 4)
        
        # Stats
        spacing = 40
        padding = 50
        small_padding = padding // 2
        stat_pos_x = panel_rect.left + padding
        stat_pos_y = panel_rect.top + small_padding
        
        stats = [
            f"Final Score: {self.current_score}",
            f"High Score: {self.high_score}",
            f"Max Combo: x{self.max_combo}",
            f"Accuracy: {self.get_accuracy():.1f}%",
            f"Rank: {self.get_rank()}"
        ]
        
        for i, stat in enumerate(stats):
            color = (255, 215, 0) if i == 0 else (255, 255, 255)
            stat_surf = font_text.render(stat, True, color)
            stat_rect = stat_surf.get_rect(x=stat_pos_x, y=stat_pos_y + i * spacing)
            surface.blit(stat_surf, stat_rect)
    
    def get_stats(self):
        """
        Lấy thống kê dạng dictionary
        
        Returns:
            dict: Thống kê đầy đủ
        """
        return {
            'current_score': self.current_score,
            'high_score': self.high_score,
            'combo': self.combo,
            'max_combo': self.max_combo,
            'correct': self.total_correct,
            'wrong': self.total_wrong,
            'total': self.total_patterns,
            'accuracy': self.get_accuracy(),
            'rank': self.get_rank()
        }
    
    def __str__(self):
        """String representation"""
        return (f"Score: {self.current_score} | "
                f"High: {self.high_score} | "
                f"Combo: x{self.combo} | "
                f"Accuracy: {self.get_accuracy():.1f}%")
