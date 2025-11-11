class SceneManager:
    def __init__(self, game):
        self.scenes = []
        self.game = game

    def push(self, scene):
        self.scenes.append(scene)
        scene.on_enter()

    def pop(self):
        if self.scenes:
            s = self.scenes.pop()
            s.on_exit()
    
    def replace(self, scene):
        # clear all
        while self.scenes:
            self.pop()
        self.push(scene)

    def top(self):
        return self.scenes[-1] if self.scenes else None

    def handle_events(self, events):
        # truyền events từ top -> bottom; nếu scene trả True (đã xử lý/nhận được input của nó) thì dừng, ko truyền xuống nữa.
        for scene in reversed(self.scenes):
            consumed = scene.handle_events(events)
            if consumed:
                break

    def update(self, dt):
        # cập nhật từ bottom -> top, chỉ scene không paused được update
        for scene in self.scenes:
            if not getattr(scene, "paused", False):
                scene.update(dt)

    def draw(self, screen):
        # vẽ từ bottom -> top, để scene trên cùng vẽ cuối cùng (che trên)
        for scene in self.scenes:
            scene.draw(screen)

    # Một hàm gọi gộp cho vòng lặp chính, hàm này sẽ được gọi trong vòng loop chính của game
    def run_frame(self, dt, events, screen):
        if not self.game.running: return
        self.handle_events(events)
        self.update(dt)
        self.draw(screen)