class Scene:
    def __init__(self, game, name=None):
        from main import Game
        self.paused = False
        self.game : Game = game # game is the Game class
        self.name = name
    
    # Trả về True nếu event bị tiêu thụ/tiếp nhận/đã xử lý và không muốn truyền xuống scene dưới
    def handle_events(self, events):
        return False
    def update(self, dt): pass
    def draw(self, screen): pass
    def on_enter(self): pass
    def on_exit(self): pass