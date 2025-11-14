import pygame
import random
import string
from Codes.Mechanics.Chatbox.Chatbox import Chatbox

class ChatboxSpawner:
    def __init__(self, spawn_interval=2.0, chatbox_lifetime=4.0):
        """
        base_sprites: danh sách các sprite (ít nhất 3 loại)
        spawn_interval: thời gian giữa các lượt spawn
        chatbox_lifetime: thời gian tồn tại của mỗi chatbox
        """
        self.base_sprites = [
            pygame.image.load("Assets/Images/Elements/Chatbox/chatbox1.png").convert_alpha(),
            pygame.image.load("Assets/Images/Elements/Chatbox/chatbox2.png").convert_alpha(),
            pygame.image.load("Assets/Images/Elements/Chatbox/chatbox3.png").convert_alpha(),
            pygame.image.load("Assets/Images/Elements/Chatbox/chatbox4.png").convert_alpha(),
            pygame.image.load("Assets/Images/Elements/Chatbox/chatbox5.png").convert_alpha(),
            pygame.image.load("Assets/Images/Elements/Chatbox/chatbox6.png").convert_alpha(),
        ]

        self.spawn_interval = spawn_interval
        self.chatbox_lifetime = chatbox_lifetime

        self.chatboxes: list[Chatbox] = []
        self.time_since_last_spawn = 0.0

    def _generate_random_text(self, max_length=6):
        # Các ký tự từ A-Z + 0-9 + ký tự đặc biệt
        return ''.join(random.choices(string.ascii_uppercase + string.digits + string.punctuation, 
                                        k=random.randint(3, max_length)))

    def _spawn_chatboxes(self):
        """Tạo ra 3 chatbox mỗi lượt."""
        self.chatboxes.clear()  # xóa hết chatbox cũ

        for i in range(3):
            sprite = self.base_sprites[i % len(self.base_sprites)]
            text = self._generate_random_text(6)
            pos = pygame.Vector2(50 + i * 150, 400)  # for position testing
            chatbox = Chatbox(base_sprite=sprite, text=text, pos=pos, lifetime=self.chatbox_lifetime)
            self.chatboxes.append(chatbox)

    def update(self, dt):
        # Sinh chatbox lần đầu nếu chưa có
        if not self.chatboxes:
            self._spawn_chatboxes()
            return
        
        self.time_since_last_spawn += dt

        # Sinh chatbox mới sau mỗi chu kỳ
        if self.time_since_last_spawn >= (self.spawn_interval + self.chatbox_lifetime):
            self.time_since_last_spawn = 0.0
            self._spawn_chatboxes()

        # Cập nhật từng chatbox
        for chatbox in self.chatboxes[:]:
            chatbox.update(dt)
            if chatbox.is_dead():
                self.chatboxes.remove(chatbox)

    def handle_events(self, events):
        if not self.chatboxes:
            return False
        for i in range(0, len(self.chatboxes)):
            if not self.chatboxes[i]:
                continue
            self.chatboxes[i].handle_events(events, i)

    def draw(self, surface):
        if not self.chatboxes:
            return
        for chatbox in self.chatboxes:
            chatbox.draw(surface)
