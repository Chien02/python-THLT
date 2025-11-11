class ScoreSystem:
    def __init__(self):
        self.current_score = 0
        self.highest_score = 0

    def add_score(self, points):
        self.current_score += points
    
    def subtract_score(self, points):
        self.current_score -= points
        if self.current_score < 0:
            self.current_score = 0

    def reset_score(self):
        self.current_score = 0

    def get_score(self):
        return self.current_score
    
    def update_highest_score(self):
        if self.current_score > self.highest_score:
            self.highest_score = self.current_score
    
    def get_highest_score(self):
        return self.highest_score