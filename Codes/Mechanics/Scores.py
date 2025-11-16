import pygame
import json
import os

class Score:
    """
    Class quản lý điểm số cho game
    - Cộng điểm khi nhập đúng
    - Trừ điểm khi nhập sai
    - Lưu high score
    - Hiển thị điểm và combo
    """
    
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
        self.score_popup = None  # (text, timer, color)
        self.popup_duration = 1.0  # 1 giây
        
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
        
        # Cập nhật high score
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self._save_high_score()
        
        # Tạo popup hiển thị điểm
        if combo_bonus > 0:
            popup_text = f"+{total_points} (Combo x{self.combo}!)"
        else:
            popup_text = f"+{total_points}"
        
        self.score_popup = (popup_text, self.popup_duration, (0, 255, 0))
        
        return total_points
    
    def add_wrong(self):
        """
        Trừ điểm khi nhập sai
        
        Returns:
            int: Số điểm bị trừ (số âm)
        """
        self.combo = 0  # Reset combo
        self.total_wrong += 1
        self.total_patterns += 1
        
        points = self.wrong_points
        self.current_score = max(0, self.current_score + points)  # Không cho điểm âm
        
        # Tạo popup hiển thị điểm bị trừ
        self.score_popup = (f"{points}", self.popup_duration, (255, 0, 0))
        
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
        Cập nhật animations (popup)
        
        Args:
            dt: Delta time
        """
        if self.score_popup:
            text, timer, color = self.score_popup
            timer -= dt
            if timer <= 0:
                self.score_popup = None
            else:
                self.score_popup = (text, timer, color)
    
    def draw(self, surface, x=20, y=20):
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
        score_text = f"Score: {self.current_score}"
        score_surf = font_large.render(score_text, True, (255, 255, 255))
        
        # Background cho score
        score_rect = score_surf.get_rect(topleft=(x, y))
        bg_rect = score_rect.inflate(20, 10)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(surface, (255, 215, 0), bg_rect, 2)
        
        surface.blit(score_surf, score_rect)
        
        # High score
        high_score_text = f"Best: {self.high_score}"
        high_score_surf = font_small.render(high_score_text, True, (255, 215, 0))
        surface.blit(high_score_surf, (x + 5, y + 50))
        
        # Combo
        if self.combo > 0:
            combo_text = f"Combo: x{self.combo}"
            combo_color = (255, 100, 100) if self.combo >= 5 else (255, 255, 255)
            combo_surf = font_medium.render(combo_text, True, combo_color)
            
            combo_rect = combo_surf.get_rect(topleft=(x, y + 80))
            combo_bg = combo_rect.inflate(15, 8)
            pygame.draw.rect(surface, (0, 0, 0, 180), combo_bg)
            if self.combo >= 5:
                pygame.draw.rect(surface, (255, 100, 100), combo_bg, 2)
            
            surface.blit(combo_surf, combo_rect)
        
        # Accuracy
        accuracy_text = f"Accuracy: {self.get_accuracy():.1f}%"
        accuracy_surf = font_small.render(accuracy_text, True, (100, 200, 255))
        surface.blit(accuracy_surf, (x + 5, y + 120))
        
        # Rank
        rank = self.get_rank()
        rank_colors = {
            'S': (255, 215, 0),   # Gold
            'A': (255, 100, 100), # Red
            'B': (100, 150, 255), # Blue
            'C': (100, 255, 150), # Green
            'D': (200, 200, 200), # Gray
            'F': (100, 100, 100)  # Dark gray
        }
        rank_text = f"Rank: {rank}"
        rank_surf = font_medium.render(rank_text, True, rank_colors.get(rank, (255, 255, 255)))
        surface.blit(rank_surf, (x, y + 145))
        
        # Score popup (animation khi cộng/trừ điểm)
        if self.score_popup:
            text, timer, color = self.score_popup
            # Fade out effect
            alpha = int((timer / self.popup_duration) * 255)
            popup_surf = font_large.render(text, True, color)
            popup_surf.set_alpha(alpha)
            
            # Vị trí di chuyển lên trên
            offset_y = int((1 - timer / self.popup_duration) * 50)
            popup_pos = (x + 200, y + 20 - offset_y)
            
            surface.blit(popup_surf, popup_pos)
    
    def draw_summary(self, surface, screen_width, screen_height):
        """
        Vẽ bảng tổng kết khi kết thúc game
        
        Args:
            surface: Pygame surface
            screen_width, screen_height: Kích thước màn hình
        """
        font_title = pygame.font.Font(None, 64)
        font_text = pygame.font.Font(None, 36)
        
        # Background overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Panel
        panel_width = 500
        panel_height = 400
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, (30, 30, 50), panel_rect)
        pygame.draw.rect(surface, (255, 215, 0), panel_rect, 4)
        
        # Title
        title_text = "GAME OVER"
        title_surf = font_title.render(title_text, True, (255, 215, 0))
        title_rect = title_surf.get_rect(centerx=screen_width // 2, y=panel_y + 30)
        surface.blit(title_surf, title_rect)
        
        # Stats
        y_offset = panel_y + 120
        spacing = 50
        
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
            stat_rect = stat_surf.get_rect(centerx=screen_width // 2, y=y_offset + i * spacing)
            surface.blit(stat_surf, stat_rect)
        
        # Hint
        hint_text = "Press ENTER to continue"
        hint_surf = pygame.font.Font(None, 24).render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surf.get_rect(centerx=screen_width // 2, y=panel_y + panel_height - 40)
        surface.blit(hint_surf, hint_rect)
    
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


# ===== DEMO =====
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Score System Demo")
    clock = pygame.time.Clock()
    
    # Tạo score manager
    score = Score(correct_points=10, wrong_points=-5)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Test: Cộng điểm
                    points = score.add_correct()
                    print(f"Correct! +{points} points")
                    print(score)
                elif event.key == pygame.K_x:
                    # Test: Trừ điểm
                    points = score.add_wrong()
                    print(f"Wrong! {points} points")
                    print(score)
                elif event.key == pygame.K_r:
                    # Reset
                    score.reset()
                    print("Score reset!")
                elif event.key == pygame.K_s:
                    # Show summary
                    print("\n=== STATS ===")
                    for key, value in score.get_stats().items():
                        print(f"{key}: {value}")
        
        # Update
        score.update(dt)
        
        # Draw
        screen.fill((20, 20, 40))
        score.draw(screen, 20, 20)
        
        # Instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "SPACE: Add correct (+10)",
            "X: Add wrong (-5)",
            "R: Reset score",
            "S: Show stats"
        ]
        for i, inst in enumerate(instructions):
            text_surf = font.render(inst, True, (200, 200, 200))
            screen.blit(text_surf, (20, 400 + i * 30))
        
        pygame.display.flip()
    
    pygame.quit()