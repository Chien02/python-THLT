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

        # Định nghĩa các tập ký tự
        self.letters = string.ascii_lowercase  # a-z
        self.digits = string.digits  # 0-9
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/"
        
        # Tỉ lệ xuất hiện
        self.SPECIAL_CHAR_RATE = 0.05  # 5% có ký tự đặc biệt
        self.NUMBER_RATE = 0.10  # 10% có số
        self.LETTER_ONLY_RATE = 0.85  # 85% chỉ chữ cái

    def _generate_random_text(self, min_length=3, max_length=5):
        """
        Generate random text theo tỉ lệ:
        - 5%: Text có ký tự đặc biệt
        - 10%: Text có số
        - 85%: Text chỉ có chữ cái
        
        Args:
            min_length: Độ dài tối thiểu
            max_length: Độ dài tối đa
            
        Returns:
            str: Text đã generate
        """
        # Quyết định loại text dựa trên xác suất
        rand = random.random()
        
        if rand < self.SPECIAL_CHAR_RATE:
            # 5%: Text có ký tự đặc biệt
            return self._generate_with_special_chars(min_length, max_length)
        elif rand < self.SPECIAL_CHAR_RATE + self.NUMBER_RATE:
            # 10%: Text có số
            return self._generate_with_numbers(min_length, max_length)
        else:
            # 85%: Text chỉ có chữ cái
            return self._generate_letters_only(min_length, max_length)
    
    def _generate_letters_only(self, min_length, max_length):
        """Generate text chỉ có chữ cái (a-z)"""
        length = random.randint(min_length, max_length)
        return ''.join(random.choice(self.letters) for _ in range(length))
    
    def _generate_with_numbers(self, min_length, max_length):
        """
        Generate text có chứa số
        Ví dụ: "abc123", "hello42", "test1"
        """
        length = random.randint(min_length, max_length)
        
        # Quyết định số lượng chữ số (1-3 số)
        num_digits = random.randint(1, min(3, length))
        num_letters = length - num_digits
        
        # Tạo các ký tự
        letters_part = [random.choice(self.letters) for _ in range(num_letters)]
        digits_part = [random.choice(self.digits) for _ in range(num_digits)]
        
        # Quyết định vị trí của số
        position = random.choice(['end', 'start', 'middle', 'mixed'])
        
        if position == 'end':
            # Số ở cuối: "hello123"
            result = letters_part + digits_part
        elif position == 'start':
            # Số ở đầu: "123hello"
            result = digits_part + letters_part
        elif position == 'middle':
            # Số ở giữa: "he123llo"
            mid = len(letters_part) // 2
            result = letters_part[:mid] + digits_part + letters_part[mid:]
        else:
            # Trộn ngẫu nhiên
            result = letters_part + digits_part
            random.shuffle(result)
        
        return ''.join(result)
    
    def _generate_with_special_chars(self, min_length, max_length):
        """
        Generate text có chứa ký tự đặc biệt
        Ví dụ: "hello!", "test@123", "#hello"
        """
        length = random.randint(min_length, max_length)
        
        # Quyết định số lượng ký tự đặc biệt (1-2 ký tự)
        num_special = random.randint(1, min(2, length))
        remaining = length - num_special
        
        # 30% có cả số
        has_numbers = random.random() < 0.3
        
        if has_numbers and remaining >= 2:
            num_digits = random.randint(1, min(2, remaining))
            num_letters = remaining - num_digits
            
            letters_part = [random.choice(self.letters) for _ in range(num_letters)]
            digits_part = [random.choice(self.digits) for _ in range(num_digits)]
            normal_chars = letters_part + digits_part
        else:
            normal_chars = [random.choice(self.letters) for _ in range(remaining)]
        
        special_part = [random.choice(self.special_chars) for _ in range(num_special)]
        
        # Quyết định vị trí ký tự đặc biệt
        position = random.choice(['start', 'end', 'mixed'])
        
        if position == 'start':
            # Ký tự đặc biệt ở đầu: "!hello", "@test"
            result = special_part + normal_chars
        elif position == 'end':
            # Ký tự đặc biệt ở cuối: "hello!", "test@"
            result = normal_chars + special_part
        else:
            # Trộn ngẫu nhiên
            result = normal_chars + special_part
            random.shuffle(result)
        
        return ''.join(result)
    
    def _spawn_chatboxes(self):
        """Tạo ra 3 chatbox mỗi lượt."""
        self.chatboxes.clear()  # xóa hết chatbox cũ

        for i in range(3):
            sprite = self.base_sprites[i % len(self.base_sprites)]
            text = self._generate_random_text()
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
