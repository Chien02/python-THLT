class Scene:
    def __init__(self, game):
        self.paused = False
        self.game = game # game is the Game class
    
    # Trả về True nếu event bị tiêu thụ/tiếp nhận/đã xử lý và không muốn truyền xuống scene dưới
    def handle_events(self, events):
        return False
    def update(self, dt): pass
    def draw(self, screen): pass
    def on_enter(self): pass
    def on_exit(self): pass